from fastapi import APIRouter
from pydantic import BaseModel

from app.runtime.execute_goal import run_goal

router = APIRouter(prefix="/agentos", tags=["AgentOS Goal"])


class GoalRequest(BaseModel):
    goal: str
    mode: str = "execute"
    approval: str = "auto"
    risk_limit: str = "normal"


@router.post("/execute-goal")
def execute_goal(req: GoalRequest):
    return run_goal(
        goal=req.goal,
        mode=req.mode,
        approval=req.approval,
        risk_limit=req.risk_limit,
    )
