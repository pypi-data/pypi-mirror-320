from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from re import M
from typing import Any

import anyio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic_core import to_json

from .cache import get_cached_tools, save_tools_cache
from .config import AppConfig, MCPServerConfig


@dataclass
class McpTool:
    toolkit_name: str
    name: str
    description: str
    args_schema: dict[str, Any]
    session: ClientSession | None
    client: MCPClient

    async def _arun(self, **kwargs: Any) -> str:
        if not self.session:
            self.session = await self.client.connect()

        result = await self.session.call_tool(self.name, **kwargs)
        content = to_json(result.content).decode()
        if result.isError:
            raise Exception(content)
        return content


@dataclass
class MCPClient:
    name: str
    _server_params: StdioServerParameters
    _tools: list[McpTool] = field(default_factory=list)
    _session: ClientSession | None = None
    _init_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _exit_stack: AsyncExitStack = field(default_factory=AsyncExitStack)

    async def connect(self) -> ClientSession:
        async with self._init_lock:
            if hasattr(self, "_session") and self._session:
                return self._session

            (read, write) = await self._exit_stack.enter_async_context(stdio_client(self._server_params))
            self._session = await self._exit_stack.enter_async_context(ClientSession(read, write))
            assert self._session
            await self._session.initialize()
            return self._session

    async def call_tool(self, tool_name: str, **kwargs: Any) -> str:
        self._session = await self.connect()
        result = await self._session.call_tool(tool_name, kwargs)
        content = to_json(result.content).decode()
        if result.isError:
            raise Exception(content)
        return content

    async def close(self) -> None:
        """Clean up resources"""
        try:
            await self._exit_stack.aclose()
        except Exception:
            pass

    async def initialize(self, force_refresh: bool = False) -> list[McpTool]:
        if self._tools and not force_refresh:
            return self._tools

        cached_tools = get_cached_tools(self._server_params)
        if cached_tools and not force_refresh:
            self._tools = [
                McpTool(
                    toolkit_name=self.name,
                    name=tool.name,
                    description=tool.description if tool.description else "",
                    args_schema=tool.inputSchema,
                    session=self._session,
                    client=self,
                )
                for tool in cached_tools
            ]
            return self._tools

        self._session = await self.connect()
        tools: types.ListToolsResult = await self._session.list_tools()
        save_tools_cache(self._server_params, tools.tools)
        self._tools = [
            McpTool(
                toolkit_name=self.name,
                name=tool.name,
                description=tool.description if tool.description else "",
                args_schema=tool.inputSchema,
                session=self._session,
                client=self,
            )
            for tool in tools.tools
        ]
        return self._tools

    @property
    def tools(self) -> list[McpTool]:
        return self._tools


async def convert_to_mcp_client(config: MCPServerConfig, force_refresh: bool = False) -> MCPClient:
    try:
        client = MCPClient(config.name, config.server_params)
        await client.initialize(force_refresh=force_refresh)
        return client
    except Exception:
        raise


async def load_tools(
    server_configs: list[MCPServerConfig], force_refresh: bool = False
) -> tuple[list[MCPClient], list[McpTool]]:
    clients = []
    tools = []

    async def convert_tools(config: MCPServerConfig) -> None:
        client = await convert_to_mcp_client(config, force_refresh)
        clients.append(client)
        tools.extend(client.tools)

    async with anyio.create_task_group() as tg:
        for config in server_configs:
            tg.start_soon(convert_tools, config)

    return clients, tools
