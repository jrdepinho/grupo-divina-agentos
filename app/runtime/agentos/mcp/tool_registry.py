from __future__ import annotations

from app.runtime.agentos.mcp.tool import MCPTool


class MCPToolRegistry:

    def __init__(self):
        self.tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        self.tools[tool.name] = tool

    def get(self, name: str):
        return self.tools.get(name)

    def exists(self, name: str):
        return name in self.tools

    def list(self):
        return list(self.tools.values())
