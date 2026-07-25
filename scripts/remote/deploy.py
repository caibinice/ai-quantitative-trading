from __future__ import annotations

import base64
import hashlib
import json
import secrets
import socket
import subprocess
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote_plus

from remote_client import ROOT_DIR, STATE_DIR, RemoteClient, read_credentials

APP_ROOT = "/opt/ai-quantitative-trading"
DEFAULT_WATCHLIST = (
    "000001,000333,000651,000858,002415,002594,300750,600000,"
    "600036,600276,600519,601318,601398,601857,601899"
)


def build_archive(release_id: str) -> Path:
    STATE_DIR.mkdir(exist_ok=True)
    archive = STATE_DIR / f"{release_id}.tar.gz"
    tracked = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT_DIR,
    ).decode("utf-8").split("\0")
    files = {Path(item) for item in tracked if item}
    dist = ROOT_DIR / "frontend" / "dist"
    if not (dist / "index.html").exists():
        raise RuntimeError("frontend/dist 不存在，请先运行前端生产构建。")
    files.update(path.relative_to(ROOT_DIR) for path in dist.rglob("*") if path.is_file())

    with tarfile.open(archive, "w:gz") as bundle:
        for relative in sorted(files, key=lambda path: path.as_posix()):
            source = ROOT_DIR / relative
            if source.is_file():
                bundle.add(source, arcname=relative.as_posix(), recursive=False)
    return archive


def build_app_env(public_ip: str, blog_admin_token: str) -> bytes:
    credentials = read_credentials()
    mysql = credentials["mysql.remote"]
    llm = credentials["deepseek.api"]
    database_url = (
        f"mysql+pymysql://{quote_plus(mysql['user'])}:{quote_plus(mysql['password'])}"
        f"@{mysql['host']}:{mysql.get('port', '3306')}/{mysql['database']}"
        f"?charset={mysql.get('charset', 'utf8mb4')}"
    )
    values = {
        "APP_ENV": "production",
        "ROOT_PATH": "/quant",
        "DATABASE_URL": database_url,
        "DATABASE_ECHO": "false",
        "CORS_ORIGINS": f"https://{public_ip}",
        "LLM_ENABLED": "true" if llm.get("api-key") else "false",
        "LLM_BASE_URL": llm.get("base-url", "https://api.deepseek.com"),
        "LLM_API_KEY": llm.get("api-key", ""),
        "LLM_API_KEY_BACKUP": llm.get("api-key-backup", ""),
        "LLM_MODEL": llm.get("model", "deepseek-v4-pro"),
        "LLM_THINKING_ENABLED": "true",
        "LLM_REASONING_EFFORT": "high",
        "SCHEDULER_ENABLED": "true",
        "DEFAULT_WATCHLIST": DEFAULT_WATCHLIST,
        "PRICE_SYNC_CRON": "20 18 * * 1-5",
        "SCORE_CRON": "40 19 * * 1-5",
        "INFRASTRUCTURE_CRON": "10 8 * * 6",
        "DATA_QUALITY_CRON": "10 20 * * 1-5",
        "BLOG_ADMIN_TOKEN": blog_admin_token,
        "BLOG_NEWS_CACHE_SECONDS": "1800",
        "BLOG_NEWS_STALE_SECONDS": "86400",
        "BLOG_NEWS_SEED_FILE": f"{APP_ROOT}/shared/blog-news-seed.json",
    }
    return "".join(f"{key}={value}\n" for key, value in values.items()).encode()


def load_or_create_web_auth() -> tuple[str, str]:
    path = STATE_DIR / "web-auth.json"
    credentials = read_credentials()
    configured = credentials["web.auth"] if credentials.has_section("web.auth") else {}
    if configured.get("username") and configured.get("password"):
        value = {
            "username": configured["username"],
            "password": configured["password"],
        }
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        return value["username"], value["password"]
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8"))
        return value["username"], value["password"]
    value = {
        "username": "quantadmin",
        "password": secrets.token_urlsafe(18),
    }
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    return value["username"], value["password"]


def load_or_create_blog_admin_token() -> str:
    path = STATE_DIR / "blog-admin.json"
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("token"):
            return value["token"]
    value = {"token": secrets.token_urlsafe(32)}
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    blog_state = ROOT_DIR.parent / "ai-blog" / ".deploy"
    if blog_state.parent.exists():
        blog_state.mkdir(exist_ok=True)
        (blog_state / "blog-admin.json").write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return value["token"]


def build_blog_news_seed() -> bytes:
    sys.path.insert(0, str(ROOT_DIR / "backend"))
    import httpx

    from app.services.blog_news import FEEDS, parse_feed

    items = []
    with httpx.Client(
        proxy="http://127.0.0.1:20808",
        timeout=30,
        follow_redirects=True,
    ) as client:
        for source, url in FEEDS:
            response = client.get(url)
            response.raise_for_status()
            parsed = parse_feed(response.text, source)
            if not parsed:
                raise RuntimeError(f"Official feed produced no items: {source}")
            items.extend(item.as_dict() for item in parsed[:40])
    payload = {
        "updatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "items": items,
    }
    return json.dumps(payload, ensure_ascii=False).encode()


def htpasswd(username: str, password: str) -> bytes:
    digest = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
    return f"{username}:{{SHA}}{digest}\n".encode()


def main() -> None:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT_DIR, text=True
    ).strip()
    release_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S") + f"-{commit}"
    archive = build_archive(release_id)
    credentials = read_credentials()
    ssh = credentials["remote.ssh"]
    public_ip = socket.gethostbyname(ssh["host"])
    username, password = load_or_create_web_auth()
    blog_admin_token = load_or_create_blog_admin_token()

    remote = RemoteClient()
    archive_remote = f"/tmp/ai-quant-{release_id}.tar.gz"
    env_remote = f"/tmp/ai-quant-{release_id}.env"
    auth_remote = f"/tmp/ai-quant-{release_id}.htpasswd"
    news_remote = f"/tmp/ai-quant-{release_id}-blog-news.json"
    wrapper_remote = f"/tmp/ai-quant-{release_id}.sh"
    release_remote = f"{APP_ROOT}/releases/{release_id}"
    try:
        print(f"Uploading release {release_id}...")
        remote.upload_file(archive, archive_remote)
        remote.upload_bytes(build_app_env(public_ip, blog_admin_token), env_remote)
        remote.upload_bytes(htpasswd(username, password), auth_remote)
        remote.upload_bytes(build_blog_news_seed(), news_remote, 0o644)
        wrapper = f"""#!/usr/bin/env bash
set -euo pipefail
mkdir -p {APP_ROOT}/releases {APP_ROOT}/shared
mkdir -p {release_remote}
tar -xzf {archive_remote} -C {release_remote}
install -m 600 {env_remote} {APP_ROOT}/shared/app.env
install -m 640 {auth_remote} {APP_ROOT}/shared/htpasswd
install -m 644 {news_remote} {APP_ROOT}/shared/blog-news-seed.json
chmod +x {release_remote}/deploy/remote/*.sh
bash {release_remote}/deploy/remote/install.sh \
  {APP_ROOT} {release_remote} {ssh['user']} {public_ip}
rm -f {archive_remote} {env_remote} {auth_remote} {news_remote} {wrapper_remote}
"""
        remote.upload_bytes(wrapper.encode(), wrapper_remote, 0o700)
        remote.run(f"/bin/bash {wrapper_remote}", root=True, timeout=2400)
        remote.run(
            f"/bin/bash {APP_ROOT}/current/deploy/remote/control.sh resources",
            root=True,
            timeout=60,
        )
    finally:
        remote.close()
        archive.unlink(missing_ok=True)

    print(f"PUBLIC_URL=https://{public_ip}/quant/")
    print(f"WEB_USERNAME={username}")
    print(f"WEB_PASSWORD_FILE={STATE_DIR / 'web-auth.json'}")
    print(f"BLOG_ADMIN_TOKEN_FILE={STATE_DIR / 'blog-admin.json'}")
    print(f"RELEASE={release_id}")


if __name__ == "__main__":
    main()
