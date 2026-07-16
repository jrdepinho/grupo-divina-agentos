from __future__ import annotations

import os
import subprocess

from agentos.developer.security import PROJECT_ROOT


def _run(*args: str, timeout: int = 120) -> dict:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def status() -> dict:
    return _run("status", "--short", "--branch")


def diff() -> dict:
    return _run("diff", "--")


def commit(message: str, approved: bool = False) -> dict:
    if not approved:
        raise PermissionError("Commit exige approved=true.")

    if os.getenv("AGENTOS_ALLOW_GIT_WRITE") != "1":
        raise PermissionError(
            "Commit bloqueado. Defina AGENTOS_ALLOW_GIT_WRITE=1 no serviço."
        )

    add_result = _run("add", "--", "agentos", "app", "tests")

    if not add_result["success"]:
        return add_result

    return _run("commit", "-m", message)


def push(approved: bool = False) -> dict:
    if not approved:
        raise PermissionError("Push exige approved=true.")

    if os.getenv("AGENTOS_ALLOW_GIT_WRITE") != "1":
        raise PermissionError(
            "Push bloqueado. Defina AGENTOS_ALLOW_GIT_WRITE=1 no serviço."
        )

    return _run("push", timeout=180)
