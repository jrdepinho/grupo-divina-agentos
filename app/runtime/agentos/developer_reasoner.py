from __future__ import annotations

from app.runtime.agentos.models import (
    Candidate,
    ExecutionAction,
    ExecutionPlan,
    GoalAnalysis,
)


class DeveloperReasoner:

    def plan(
        self,
        analysis: GoalAnalysis,
        candidates: list[Candidate],
        project_context: dict,
    ) -> ExecutionPlan:

        plan = ExecutionPlan()

        if not candidates:
            plan.reasoning = "Nenhum candidato encontrado."
            return plan

        best = candidates[0]

        if analysis.intent == "patch":

            plan.actions.append(
                ExecutionAction(
                    capability="code.patch_file",
                    arguments={
                        "path": best.path,
                        "search": "",
                        "replace": "",
                    },
                )
            )

        elif analysis.intent == "create":

            plan.actions.append(
                ExecutionAction(
                    capability="code.write_file",
                    arguments={
                        "path": best.path,
                        "content": "",
                        "overwrite": False,
                    },
                )
            )

        plan.confidence = best.score / 10.0
        plan.reasoning = (
            f"Melhor candidato: {best.path}"
        )

        return plan
