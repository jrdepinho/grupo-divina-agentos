from __future__ import annotations

from typing import Any

from app.runtime.agentos.execution.dispatcher_v2 import DispatcherV2
from app.runtime.agentos.memory import ExecutionSession
from app.runtime.agentos.orchestrator.pipeline_builder import PipelineBuilder
from app.runtime.agentos.bootstrap import initialize
from app.runtime.agentos.project_intelligence import ProjectIntelligence


RISK_LEVELS = {
    "low": 1,
    "normal": 2,
    "medium": 2,
    "high": 3,
    "critical": 4,
    "unknown": 4,
}

APPROVED_VALUES = {
    "approved",
    "approve",
    "confirm",
    "confirmed",
    "confirmado",
    "autorizado",
    "yes",
    "sim",
}


def _risk_value(value: str) -> int:
    return RISK_LEVELS.get(str(value or "").lower(), 4)


def _plan_risk(plan: list[dict[str, Any]]) -> str:
    highest_name = "low"
    highest_value = 1

    for step in plan:
        risk = step.get("metadata", {}).get("risk", "unknown")
        value = _risk_value(risk)

        if value > highest_value:
            highest_name = risk
            highest_value = value

    return highest_name


def _approval_required(plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        step
        for step in plan
        if step.get("metadata", {}).get("requires_approval", False)
    ]


def run(
    goal: str,
    mode: str = "execute",
    approval: str = "auto",
    risk_limit: str = "normal",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:

    initialize()

    if context is None:
        context = ProjectIntelligence().build_context(goal)

    session = ExecutionSession(
        goal=goal,
        mode=mode,
        approval=approval,
        risk_limit=risk_limit,
    )

    builder = PipelineBuilder()
    dispatcher = DispatcherV2()

    plan = builder.build(
        goal=goal,
        context=context,
    )
    session.plan = plan

    calculated_risk = _plan_risk(plan)
    approval_steps = _approval_required(plan)

    session.add_event(
        "plan.created",
        {
            "steps": len(plan),
            "risk": calculated_risk,
            "approval_required": bool(approval_steps),
        },
    )

    base_report = {
        "goal": goal,
        "mode": mode,
        "approval": approval,
        "risk_limit": risk_limit,
        "calculated_risk": calculated_risk,
        "plan": plan,
        "context": context,
    }

    if mode.lower() == "plan":
        session.add_event(
            "execution.skipped",
            {"reason": "Modo de planejamento."},
        )
        session.finish()

        return {
            "ok": True,
            "status": "planned",
            "goal": goal,
            "approval_required": bool(approval_steps),
            "executed": False,
            "session_id": session.session_id,
        }

    if _risk_value(calculated_risk) > _risk_value(risk_limit):
        session.add_event(
            "execution.blocked",
            {
                "reason": "Risco acima do limite permitido.",
                "calculated_risk": calculated_risk,
                "risk_limit": risk_limit,
            },
        )
        session.finish()

        return {
            "ok": False,
            "status": "blocked_by_risk",
            "goal": goal,
            "executed": False,
            "error": (
                f"Risco calculado '{calculated_risk}' excede "
                f"o limite '{risk_limit}'."
            ),
            "session_id": session.session_id,
        }

    approval_normalized = str(approval or "").strip().lower()

    if approval_steps and approval_normalized not in APPROVED_VALUES:
        session.add_event(
            "execution.blocked",
            {
                "reason": "Aprovação explícita necessária.",
                "actions": [
                    step["action"]
                    for step in approval_steps
                ],
            },
        )
        session.finish()

        return {
            "ok": False,
            "status": "approval_required",
            "goal": goal,
            "executed": False,
            "approval_required": True,
            "error": "O plano contém ações que exigem aprovação explícita.",
            "session_id": session.session_id,
        }

    session.add_event(
        "execution.started",
        {"steps": len(plan)},
    )

    execution = dispatcher.execute(plan)

    session.add_event(
        "execution.finished",
        {
            "ok": execution.get("ok", False),
            "executed_steps": execution.get("executed_steps", 0),
            "failed_steps": execution.get("failed_steps", 0),
        },
    )
    session.finish()

    return {
        "ok": execution.get("ok", False),
        "status": "completed" if execution.get("ok") else "failed",
        "goal": goal,
        "executed": True,
        "executed_steps": execution.get("executed_steps", 0),
        "failed_steps": execution.get("failed_steps", 0),
        "session_id": session.session_id,
    }
