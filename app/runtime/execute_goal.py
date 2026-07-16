from app.runtime.agentos.background import execute_async


def run_goal(
    goal,
    mode="execute",
    approval="auto",
    risk_limit="normal",
    context=None,
):
    return execute_async(
        goal=goal,
        mode=mode,
        approval=approval,
        risk_limit=risk_limit,
        context=context,
    )
