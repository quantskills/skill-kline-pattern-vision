"""Read-only PandaData adapter. Credentials are loaded only at runtime."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping

ENV_FILE = Path.home() / ".pandadata" / "pandadata.env"
SENSITIVE = re.compile(r"(?i)(password|passwd|token|username|cookie)\s*[=:]\s*[^\s,;]+")


def _read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def load_credentials(environ: Mapping[str, str] | None = None, env_file: Path = ENV_FILE) -> tuple[str, str]:
    env = os.environ if environ is None else environ
    file_values = _read_env_file(env_file)
    username = env.get("PANDA_USERNAME") or file_values.get("PANDA_USERNAME") or env.get("PANDADATA_USERNAME") or file_values.get("PANDADATA_USERNAME") or ""
    password = env.get("PANDA_PASSWORD") or file_values.get("PANDA_PASSWORD") or env.get("PANDADATA_PASSWORD") or file_values.get("PANDADATA_PASSWORD") or ""
    if not username or not password:
        raise RuntimeError("缺少 PandaData 凭证。请设置运行时环境变量或写入 ~/.pandadata/pandadata.env；不要把凭证粘贴到对话或代码中。")
    return username, password


def normalize_username(username: str) -> str:
    value = username.strip()
    return "86" + value if len(value) == 11 and value.isdigit() and value.startswith("1") else value


def sanitize_error(error: Exception | str) -> str:
    text = SENSITIVE.sub(lambda m: f"{m.group(1)}=<redacted>", str(error))
    for key in ("PANDA_USERNAME", "PANDA_PASSWORD", "PANDADATA_USERNAME", "PANDADATA_PASSWORD"):
        value = os.environ.get(key)
        if value:
            text = text.replace(value, "<redacted>")
    return text[:500]


def init_pandadata():
    if sys.version_info < (3, 10):
        raise RuntimeError("需要 Python 3.10 或更高版本。")
    try:
        import panda_data
    except ModuleNotFoundError as exc:
        raise RuntimeError("未安装 panda_data，请安装 requirements.txt。") from exc
    username, password = load_credentials()
    try:
        panda_data.init_token(username=normalize_username(username), password=password)
    except Exception as exc:
        raise RuntimeError("PandaData 登录失败：" + sanitize_error(exc)) from exc
    return panda_data


def fetch_stock(symbol: str, start_date: str, end_date: str, frequency: str = "1d", fields: list[str] | None = None) -> Any:
    api = init_pandadata()
    fields = fields or []
    if frequency == "1d":
        return api.get_stock_daily(symbol=[symbol], start_date=start_date, end_date=end_date, fields=fields)
    return api.get_stock_min(symbol=[symbol], start_date=start_date, end_date=end_date, frequency=frequency, fields=fields)


def fetch_future(symbol: str, start_date: str, end_date: str, frequency: str = "1d", fields: list[str] | None = None) -> Any:
    api = init_pandadata()
    fields = fields or []
    if frequency == "1d":
        return api.get_future_daily(symbol=[symbol], start_date=start_date, end_date=end_date, fields=fields)
    return api.get_future_min(symbol=[symbol], start_date=start_date, end_date=end_date, frequency=frequency, fields=fields)
