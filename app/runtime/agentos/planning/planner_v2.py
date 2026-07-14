from __future__ import annotations

from app.runtime.agentos.planner import plan as legacy_plan
from app.runtime.agentos.capability_metadata import get_metadata


class PlannerV2:

    def build(self, goal: str):

        plan = legacy_plan(goal)

        enriched = []

        for order, step in enumerate(plan, start=1):

            meta = get_metadata(step["action"])

            enriched.append({
                "order": order,
                "action": step["action"],
                "args": step.get("args", {}),
                "metadata": meta.to_dict(),
            })

        return enriched
