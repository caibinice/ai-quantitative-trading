from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
LOCAL_CREDENTIALS_FILE = ROOT_DIR / "credentials.txt"
SHARED_CREDENTIALS_FILE = ROOT_DIR.parent / "ai-blog" / "credentials.txt"
DEFAULT_CREDENTIALS_FILE = (
    LOCAL_CREDENTIALS_FILE
    if LOCAL_CREDENTIALS_FILE.exists()
    else SHARED_CREDENTIALS_FILE
)
DEFAULT_WATCHLIST = (
    "000001,000333,000651,000858,002415,002594,300750,600000,"
    "600036,600276,600519,601318,601398,601857,601899"
)
DEFAULT_STOCK_NAMES = {
    "000001": "平安银行",
    "000333": "美的集团",
    "000651": "格力电器",
    "000858": "五粮液",
    "002415": "海康威视",
    "002594": "比亚迪",
    "300750": "宁德时代",
    "600000": "浦发银行",
    "600036": "招商银行",
    "600276": "恒瑞医药",
    "600519": "贵州茅台",
    "601318": "中国平安",
    "601398": "工商银行",
    "601857": "中国石油",
    "601899": "紫金矿业",
}


def _read_section(path: Path, target: str) -> dict[str, str]:
    """Read the tiny INI-like credentials file without logging its values."""
    if not path.exists():
        return {}
    current = ""
    common: dict[str, str] = {}
    scoped: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            continue
        if current in {target, f"quant.{target}"} and "=" in line:
            key, value = line.split("=", 1)
            destination = scoped if current.startswith("quant.") else common
            destination[key.strip()] = value.strip()
    return {**common, **scoped}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI 量化研究舱"
    app_env: str = "development"
    api_prefix: str = "/api"
    root_path: str = ""
    cors_origins: str = "http://localhost:5173"
    database_url: str = ""
    database_echo: bool = False
    credentials_file: str = str(DEFAULT_CREDENTIALS_FILE)

    llm_enabled: bool = True
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_api_key_backup: str = ""
    llm_model: str = ""
    llm_thinking_enabled: bool = True
    llm_reasoning_effort: str = "high"
    llm_timeout_seconds: int = 45

    scheduler_enabled: bool = False
    default_watchlist: str = DEFAULT_WATCHLIST
    upstream_proxy: str = ""
    price_sync_cron: str = "20 18 * * 1-5"
    score_cron: str = "40 19 * * 1-5"
    infrastructure_cron: str = "10 8 * * 6"
    data_quality_cron: str = "10 20 * * 1-5"

    blog_admin_token: str = ""
    blog_news_cache_seconds: int = 1800
    blog_news_stale_seconds: int = 86400
    blog_news_seed_file: str = ""

    action_password: str = ""
    action_token_secret: str = ""
    action_token_ttl_minutes: int = 30

    @model_validator(mode="after")
    def fill_from_credentials(self) -> Settings:
        path = Path(self.credentials_file)
        if not path.is_absolute():
            path = ROOT_DIR / path

        mysql = _read_section(path, "mysql.remote")
        if not self.database_url and mysql:
            user = quote_plus(mysql.get("user", ""))
            password = quote_plus(mysql.get("password", ""))
            host = mysql.get("host", "127.0.0.1")
            port = mysql.get("port", "3306")
            database = mysql.get("database", "ai_quantitative_trading")
            charset = mysql.get("charset", "utf8mb4")
            self.database_url = (
                f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
            )

        llm = _read_section(path, "deepseek.api")
        if not self.llm_base_url:
            self.llm_base_url = llm.get("base-url", "https://api.deepseek.com")
        if not self.llm_api_key:
            self.llm_api_key = llm.get("api-key", "")
        if not self.llm_api_key_backup:
            self.llm_api_key_backup = llm.get("api-key-backup", "")
        if not self.llm_model:
            self.llm_model = llm.get("model", "deepseek-v4-pro")
        if self.llm_reasoning_effort not in {"high", "max"}:
            self.llm_reasoning_effort = "high"

        if not self.database_url:
            self.database_url = f"sqlite:///{ROOT_DIR / 'ai_quant.db'}"
        return self

    @property
    def watchlist(self) -> list[str]:
        return [item.strip() for item in self.default_watchlist.split(",") if item.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.upstream_proxy:
        os.environ.setdefault("HTTP_PROXY", settings.upstream_proxy)
        os.environ.setdefault("HTTPS_PROXY", settings.upstream_proxy)
    return settings
