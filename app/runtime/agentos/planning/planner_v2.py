from __future__ import annotations

from app.runtime.agentos.planner import plan
from app.runtime.agentos.capability_metadata import get_metadata


class PlannerV2:

    def build(self, goal: str):

        steps = plan(goal)

        enriched = []

        for order, step in enumerate(steps, start=1):

            meta = get_metadata(step["action"])

            try:
                metadata = meta.to_dict() if meta else {}
            except Exception:
                metadata = {}

            enriched.append({
                "order": order,
                "action": step["action"],
                "args": step.get("args", {}),
                "metadata": metadata,
            })

        return enriched
