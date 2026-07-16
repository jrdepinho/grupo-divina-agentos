from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

from app.runtime.agentos.planner import plan as legacy_plan
from app.runtime.agentos.capability_metadata import get_metadata
from app.runtime.agentos.planning.strategies.development_strategy import (
    DevelopmentStrategy,
)


class PlannerV2:

    def __init__(self):
        self.dev = DevelopmentStrategy()

    def _to_dict(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, Mapping):
            return dict(value)

        if is_dataclass(value):
            return asdict(value)

        if hasattr(value, "model_dump"):
            try:
                result = value.model_dump()
                return dict(result) if isinstance(result, Mapping) else {}
            except Exception:
                return {}

        if hasattr(value, "dict"):
            try:
                result = value.dict()
                return dict(result) if isinstance(result, Mapping) else {}
            except Exception:
                return {}

        if hasattr(value, "to_dict"):
            try:
                result = value.to_dict()
                return dict(result) if isinstance(result, Mapping) else {}
            except Exception:
                return {}

        if hasattr(value, "__dict__"):
            return {
                key: val
                for key, val in vars(value).items()
                if not key.startswith("_")
            }

        return {}

    def _metadata(self, action: str) -> dict[str, Any]:
        try:
            return self._to_dict(get_metadata(action))
        except Exception:
            return {}

    def _extract_steps(self, plan: Any) -> list[Any]:
        if plan is None:
            return []

        if isinstance(plan, Mapping):
            for key in ("steps", "plan", "actions", "tasks"):
                steps = plan.get(key)
                if steps is not None:
                    return self._extract_steps(steps)

            if any(key in plan for key in ("action", "capability", "name")):
                return [plan]

            return []

        if isinstance(plan, (str, bytes)):
            return [{"action": plan.decode() if isinstance(plan, bytes) else plan}]

        if hasattr(plan, "steps"):
            return self._extract_steps(getattr(plan, "steps"))

        if isinstance(plan, Iterable):
            return list(plan)

        step = self._to_dict(plan)
        if step:
            return [step]

        return []

    def _normalize_step(self, step: Any) -> dict[str, Any]:
        if isinstance(step, (str, bytes)):
            action = step.decode() if isinstance(step, bytes) else step
            return {
                "action": action,
                "args": {},
            }

        data = self._to_dict(step)

        action = data.get("action") or data.get("capability") or data.get("name")
        if not action and hasattr(step, "action"):
            action = getattr(step, "action")

        if not action:
            raise ValueError(f"Invalid plan step without action: {step}")

        args = data.get("args")
        if args is None:
            args = data.get("params")
        if args is None:
            args = data.get("arguments")
        if args is None:
            args = {}

        return {
            "action": str(action),
            "args": args,
        }

    def _enrich(self, plan: Any) -> list[dict[str, Any]]:
        enriched = []

        for order, step in enumerate(self._extract_steps(plan), start=1):
            normalized = self._normalize_step(step)
            action = normalized["action"]

            enriched.append(
                {
                    "order": order,
                    "action": action,
                    "args": normalized["args"],
                    "metadata": self._metadata(action),
                }
            )

        return enriched

    def build(self, goal: str) -> list[dict[str, Any]]:
        if self.dev.matches(goal):
            return self._enrich(self.dev.build(goal))

        return self._enrich(legacy_plan(goal))