from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionRequest:
    capability: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionResult:
    capability: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
