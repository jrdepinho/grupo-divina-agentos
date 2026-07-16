from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GoalAnalysis:
    intent: str
    keywords: list[str]


@dataclass
class Candidate:
    path: str
    score: float
    reason: str


@dataclass
class ExecutionAction:
    capability: str
    arguments: dict[str, Any]


@dataclass
class ExecutionPlan:
    actions: list[ExecutionAction] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
