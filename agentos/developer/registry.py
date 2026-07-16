from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agentos.developer.actions.git_tools import commit, diff, push, status
from agentos.developer.actions.patch_file import execute as patch_file
from agentos.developer.actions.python_tools import compile_python, run_tests
from agentos.developer.actions.write_file import execute as write_file


CAPABILITIES: dict[str, Callable[..., dict[str, Any]]] = {
    "code.write_file": write_file,
    "code.patch_file": patch_file,
    "python.compile": compile_python,
    "tests.run": run_tests,
    "git.status": status,
    "git.diff": diff,
    "git.commit": commit,
    "git.push": push,
}

PHASE_1_CAPABILITIES = {
    "code.write_file",
    "code.patch_file",
    "python.compile",
    "tests.run",
    "git.status",
    "git.diff",
}

PHASE_2_CAPABILITIES = {
    "git.commit",
    "git.push",
}


def list_capabilities() -> list[str]:
    return sorted(CAPABILITIES)


def dispatch(capability: str, arguments: dict[str, Any]) -> dict[str, Any]:
    action = CAPABILITIES.get(capability)

    if action is None:
        raise ValueError(f"Capacidade desconhecida: {capability}")

    return action(**arguments)
