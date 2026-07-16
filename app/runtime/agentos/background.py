from concurrent.futures import ThreadPoolExecutor
import traceback
import uuid

from app.runtime.agentos.runtime.engine_v2 import run
from app.runtime.agentos.memory import ExecutionSession, save_session


_executor = ThreadPoolExecutor(max_workers=2)


def _execute(session_id, goal, mode, approval, risk_limit, context):
    print(f"[BACKGROUND] iniciando {session_id}", flush=True)

    try:
        result = run(
            goal=goal,
            mode=mode,
            approval=approval,
            risk_limit=risk_limit,
            context=context,
            session_id=session_id,
        )

        print(
            f"[BACKGROUND] terminou {session_id}: {result}",
            flush=True,
        )

    except Exception as exc:
        print(
            f"[BACKGROUND] ERRO {session_id}: {repr(exc)}",
            flush=True,
        )
        traceback.print_exc()


def execute_async(
    goal,
    mode="execute",
    approval="auto",
    risk_limit="normal",
    context=None,
):
    if mode == "plan":
        return run(
            goal=goal,
            mode=mode,
            approval=approval,
            risk_limit=risk_limit,
            context=context,
        )

    session_id = str(uuid.uuid4())

    queued_session = ExecutionSession(
        goal=goal,
        mode=mode,
        approval=approval,
        risk_limit=risk_limit,
        session_id=session_id,
    )

    queued_session.add_event(
        "execution.queued",
        {
            "status": "queued",
        },
    )

    save_session(queued_session)

    _executor.submit(
        _execute,
        session_id,
        goal,
        mode,
        approval,
        risk_limit,
        context,
    )

    return {
        "ok": True,
        "status": "queued",
        "session_id": session_id,
    }
