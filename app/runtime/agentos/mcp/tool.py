from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class MCPTool:

    name: str

    description: str

    handler: Callable

    parameters: dict | None = None

    metadata: dict | None = None
