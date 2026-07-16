from __future__ import annotations

from app.runtime.agentos.planner.planner import Planner


class PipelineBuilder:

    def __init__(self):
        self.planner = Planner()

    def build(
        self,
        goal,
        context,
    ):

        if not context or "project_context" not in context:
            raise RuntimeError(
                "PipelineBuilder recebeu contexto sem project_context."
            )

        return self.planner.build(
            goal=goal,
            context=context,
        )
