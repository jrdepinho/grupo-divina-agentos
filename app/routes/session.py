from fastapi import APIRouter, HTTPException

from app.runtime.agentos.memory import get_session

router = APIRouter(
    prefix="/agentos",
    tags=["AgentOS Session"],
)

@router.get("/session/{session_id}")
def session(session_id: str):

    s = get_session(session_id)

    if s is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada.",
        )

    return {
        "status": "finished" if s.finished_at else "running",
        "session": s.to_dict(),
        "result": s.result,
    }
