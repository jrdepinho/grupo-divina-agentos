from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.runtime.agentos.mcp.tool import MCPTool
from app.runtime.agentos.mcp.tool_registry import MCPToolRegistry


_registry = MCPToolRegistry()


@dataclass
class Capability:
    name: str
    description: str
    handler: Callable


def register(capability: Capability):

    _registry.register(
        MCPTool(
            name=capability.name,
            description=capability.description,
            handler=capability.handler,
        )
    )


def get(name: str):
    return _registry.get(name)


def exists(name: str):
    return _registry.exists(name)


def list_capabilities():
    return [tool.name for tool in _registry.list()]


def list_tools():
    return _registry.list()
