from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from mcp import StdioServerParameters, types

CACHE_DIR = Path.home() / ".cache"
CACHE_EXPIRY_HOURS = 24


def get_cached_tools(server_param: StdioServerParameters) -> list[types.Tool] | None:
    """Retrieve cached tools if available and not expired.

    Args:
        server_param (StdioServerParameters): The server parameters to identify the cache.

    Returns:
        Optional[List[types.Tool]]: A list of tools if cache is available and not expired, otherwise None.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = f"{server_param.command}-{'-'.join(server_param.args)}".replace("/", "-")
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if not cache_file.exists():
        return None

    cache_data = json.loads(cache_file.read_text())
    cached_time = datetime.fromisoformat(cache_data["cached_at"])

    if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
        return None

    return [types.Tool(**tool) for tool in cache_data["tools"]]


def save_tools_cache(server_param: StdioServerParameters, tools: list[types.Tool]) -> None:
    """Save tools to cache.

    Args:
        server_param (StdioServerParameters): The server parameters to identify the cache.
        tools (List[types.Tool]): The list of tools to be cached.
    """
    cache_key = f"{server_param.command}-{'-'.join(server_param.args)}".replace("/", "-")
    cache_file = CACHE_DIR / f"{cache_key}.json"

    cache_data = {"cached_at": datetime.now().isoformat(), "tools": [tool.model_dump() for tool in tools]}
    cache_file.write_text(json.dumps(cache_data))
