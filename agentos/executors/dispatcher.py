from agentos.executors.registry import get_executor


def dispatch(mission):

    executor_name = mission.get("type", "noop")

    executor = get_executor(executor_name)

    return executor.execute(mission)
