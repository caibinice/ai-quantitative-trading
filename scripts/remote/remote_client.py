from __future__ import annotations

import configparser
import io
import re
import secrets
import shlex
import time
from pathlib import Path

import paramiko

ROOT_DIR = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT_DIR / ".deploy"
SHARED_CREDENTIALS = ROOT_DIR.parent / "ai-blog" / "credentials.txt"


def _scoped_credentials(
    parser: configparser.ConfigParser, namespace: str
) -> configparser.ConfigParser:
    resolved = configparser.ConfigParser(interpolation=None)
    prefix = f"{namespace}."
    for section in parser.sections():
        if not section.startswith(prefix):
            resolved[section] = dict(parser[section])
    for section in parser.sections():
        if section.startswith(prefix):
            resolved[section.removeprefix(prefix)] = dict(parser[section])
    return resolved


def read_credentials() -> configparser.ConfigParser:
    local = ROOT_DIR / "credentials.txt"
    path = local if local.exists() else SHARED_CREDENTIALS
    if not path.exists():
        raise RuntimeError(
            "缺少项目 credentials.txt 和 ai-blog/credentials.txt，无法连接远程服务器。"
        )
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path, encoding="utf-8")
    return _scoped_credentials(parser, "quant")


class RemoteClient:
    def __init__(self) -> None:
        credentials = read_credentials()
        self.config = credentials["remote.ssh"]
        self.root_password = self.config.get("root_password", "")
        STATE_DIR.mkdir(exist_ok=True)
        known_hosts = STATE_DIR / "known_hosts"

        self.client = paramiko.SSHClient()
        if known_hosts.exists():
            self.client.load_host_keys(str(known_hosts))
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.config["host"],
            port=self.config.getint("port", 22),
            username=self.config["user"],
            password=self.config["password"],
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
        )
        self.client.save_host_keys(str(known_hosts))

    def close(self) -> None:
        self.client.close()

    def upload_bytes(self, content: bytes, remote_path: str, mode: int = 0o600) -> None:
        with self.client.open_sftp() as sftp:
            sftp.putfo(io.BytesIO(content), remote_path)
            sftp.chmod(remote_path, mode)

    def upload_file(self, local_path: Path, remote_path: str, mode: int = 0o600) -> None:
        with self.client.open_sftp() as sftp:
            sftp.put(str(local_path), remote_path)
            sftp.chmod(remote_path, mode)

    def run(self, command: str, *, root: bool = False, timeout: int = 1800) -> str:
        if root:
            text, code = self._run_as_root(command, timeout)
        else:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            output = stdout.read().decode("utf-8", "replace")
            error = stderr.read().decode("utf-8", "replace")
            code = stdout.channel.recv_exit_status()
            text = (output + error).strip()
        for secret in (self.config.get("password", ""), self.root_password):
            if secret:
                text = text.replace(secret, "***")
        if text:
            print(text)
        if code != 0:
            raise RuntimeError(f"远程命令失败，退出码 {code}。")
        return text

    def _run_as_root(self, command: str, timeout: int) -> tuple[str, int]:
        if not self.root_password:
            raise RuntimeError("credentials.txt 缺少 remote.ssh.root_password。")

        marker = f"__AI_QUANT_RC_{secrets.token_hex(8)}__"
        channel = self.client.invoke_shell(width=160, height=40)
        channel.settimeout(2)
        time.sleep(0.2)
        while channel.recv_ready():
            channel.recv(65535)

        wrapped = (
            f"su - root -c {shlex.quote(command)}; "
            f"printf '\\n{marker}%s\\n' \"$?\"\n"
        )
        channel.send(wrapped)
        output = ""
        password_sent = False
        deadline = time.monotonic() + timeout
        code: int | None = None

        while time.monotonic() < deadline:
            if channel.recv_ready():
                output += channel.recv(65535).decode("utf-8", "replace")
                if not password_sent and "Password:" in output:
                    channel.send(self.root_password + "\n")
                    password_sent = True
                match = re.search(re.escape(marker) + r"(\d+)", output)
                if match:
                    code = int(match.group(1))
                    break
            else:
                time.sleep(0.1)

        channel.close()
        if code is None:
            raise TimeoutError("等待远程 root 命令完成超时。")
        cleaned = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", output)
        cleaned = re.sub(r"\x1b\].*?(?:\x07|\x1b\\)", "", cleaned)
        cleaned = re.sub(r"\x1b.", "", cleaned)
        cleaned = cleaned.replace("\x00", "")
        cleaned = cleaned.replace("\r", "")
        cleaned = cleaned.replace(wrapped.strip(), "")
        cleaned = re.sub(re.escape(marker) + r"\d+", "", cleaned)
        lines = [
            line
            for line in cleaned.splitlines()
            if line.strip() != "Password:"
            and not line.startswith("su - root -c ")
            and not re.match(r"^\[[^]]+@[^]]+\][#$]\s*$", line.strip())
        ]
        return "\n".join(lines).strip(), code
