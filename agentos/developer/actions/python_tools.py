from __future__ import annotations

import subprocess
from pathlib import Path

from agentos.developer.security import PROJECT_ROOT, safe_project_path


def compile_python(paths: list[str] | None = None) -> dict:
    if paths:
        files = [safe_project_path(path) for path in paths]
    else:
        files = [
            path
            for base in (PROJECT_ROOT / "agentos", PROJECT_ROOT / "app")
            for path in base.rglob("*.py")
            if "__pycache__" not in path.parts
        ]

    command = ["python3", "-m", "py_compile", *[str(path) for path in files]]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    return {
        "success": result.returncode == 0,
        "files_checked": len(files),
        "stdout": result.stdout[-10_000:],
        "stderr": result.stderr[-10_000:],
        "returncode": result.returncode,
    }


def run_tests() -> dict:
    result = subprocess.run(
        ["python3", "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout[-20_000:],
        "stderr": result.stderr[-20_000:],
        "returncode": result.returncode,
    }
