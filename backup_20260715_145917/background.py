from app.runtime.agentos.queue import enqueue
from app.runtime.agentos.worker import start_worker
from app.runtime.agentos.runtime.engine_v2 import run


def execute_async(
    goal,
    mode="execute",
    approval="auto",
    risk_limit="normal",
    context=None,
):
    """
    Agenda uma execução em background.
    """

    start_worker()

    print(f"[BACKGROUND] ENQUEUE goal={goal}", flush=True)

    enqueue(
        lambda: run(
            goal=goal,
            mode=mode,
            approval=approval,
            risk_limit=risk_limit,
            context=context,
        )
    )

    return {
        "ok": True,
        "status": "queued",
    }
