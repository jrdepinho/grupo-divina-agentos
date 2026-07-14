from __future__ import annotations

from pathlib import Path
import subprocess
import difflib

ROOT = Path("/opt/agente-divina-v2").resolve()


def _resolve(path: str) -> Path:
    p = (ROOT / path).resolve()

    if ROOT not in p.parents and p != ROOT:
        raise ValueError("Arquivo fora do projeto.")

    return p


def search(text: str):
    matches = []

    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue

        if "__pycache__" in f.parts:
            continue

        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        if text.lower() in content.lower():
            matches.append(str(f.relative_to(ROOT)))

    return {
        "ok": True,
        "matches": matches,
    }


def read(path: str):
    p = _resolve(path)

    return {
        "ok": True,
        "path": path,
        "content": p.read_text(encoding="utf-8"),
    }


def write(path: str, content: str):
    p = _resolve(path)

    p.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "path": path,
    }


def patch(path: str, old: str, new: str):
    p = _resolve(path)

    before = p.read_text(encoding="utf-8")

    after = before.replace(old, new)

    if before == after:
        return {
            "ok": False,
            "message": "Trecho não encontrado."
        }

    p.write_text(after, encoding="utf-8")

    diff = "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm=""
        )
    )

    return {
        "ok": True,
        "diff": diff,
    }


def compile():
    proc = subprocess.run(
        ["python3","-m","compileall","-q",str(ROOT / "app")],
        capture_output=True,
        text=True,
    )

    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-15000:],
        "stderr": proc.stderr[-15000:],
    }


def validate():
    return compile()


def rollback():
    return {
        "ok": False,
        "message": "Rollback ainda não implementado."
    }

