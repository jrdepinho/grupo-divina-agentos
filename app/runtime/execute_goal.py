from app.runtime.agentos.runtime.engine_v2 import run


def run_goal(
    goal,
    mode="execute",
    approval="auto",
    context=None,
):
    return run(
        goal=goal,
        mode=mode,
        approval=approval,
        context=context,
    )
