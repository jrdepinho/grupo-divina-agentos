from agentos.executors.noop import NoopExecutor
from agentos.executors.python import PythonExecutor
from agentos.executors.http import HttpExecutor
from agentos.executors.admin import AdminExecutor

EXECUTORS = {
    "noop": NoopExecutor(),
    "python": PythonExecutor(),
    "http": HttpExecutor(),
    "admin": AdminExecutor(),
}


def get_executor(name):
    if name not in EXECUTORS:
        raise ValueError(f"Executor '{name}' não registrado.")

    return EXECUTORS[name]
