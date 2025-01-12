from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from mcp import StdioServerParameters

CONFIG_PATH = "mcp_settings.json"


@dataclass
class MCPServerConfig:
    name: str
    server_params: StdioServerParameters


@dataclass
class MCPConfig:
    """Configuration for an MCP server."""

    command: str
    args: list[str]
    env: dict[str, str]
    enabled: bool
    exclude_tools: list[str]
    requires_confirmation: list[str]

    @classmethod
    def from_dict(cls, config: dict) -> MCPConfig:
        """Create ServerConfig from dictionary."""
        return cls(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {}),
            enabled=config.get("enabled", True),
            exclude_tools=config.get("exclude_tools", []),
            requires_confirmation=config.get("requires_confirmation", []),
        )


@dataclass
class AppConfig:
    """Main application configuration."""

    mcp_servers: dict[str, MCPConfig]
    tools_requires_confirmation: list[str]

    @classmethod
    def load(cls, str_config_path: str = "") -> AppConfig:
        config_path = Path(str_config_path if str_config_path else CONFIG_PATH)
        if not config_path.exists():
            raise FileNotFoundError(f"Could not find config file in {CONFIG_PATH}")

        with config_path.open("r") as f:
            config = json.load(f)

        # Extract tools requiring confirmation
        tools_requires_confirmation = []
        for server_config in config["mcpServers"].values():
            tools_requires_confirmation.extend(server_config.get("requires_confirmation", []))

        return cls(
            mcp_servers={
                name: MCPConfig.from_dict(server_config) for name, server_config in config["mcpServers"].items()
            },
            tools_requires_confirmation=tools_requires_confirmation,
        )

    def _get_enabled_servers(self) -> dict[str, MCPConfig]:
        """Get only enabled server configurations."""
        return {name: config for name, config in self.mcp_servers.items() if config.enabled}

    @property
    def mcp_server_configs(self) -> list[MCPServerConfig]:
        """Get server configurations as MCPConfig objects."""
        return [
            MCPServerConfig(
                name,
                StdioServerParameters(
                    command=config.command, args=config.args or [], env={**(config.env or {}), **os.environ}
                ),
            )
            for name, config in self._get_enabled_servers().items()
        ]
