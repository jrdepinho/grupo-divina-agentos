from __future__ import annotations

from pathlib import Path
import subprocess
import difflib
import re

ROOT = Path("/opt/agente-divina-v2").resolve()


def _resolve(path: str) -> Path:
    p = (ROOT / path).resolve()

    if ROOT not in p.parents and p != ROOT:
        raise ValueError("Arquivo fora do projeto.")

    return p



def search(text: str):
    tokens = [
        t.lower()
        for t in re.findall(r"[a-zA-Z0-9_]+", text)
        if len(t) >= 3
    ]

    scored = []

    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue

        if "__pycache__" in f.parts:
            continue

        rel = str(f.relative_to(ROOT)).lower()

        if rel.endswith(".bak"):
            continue

        if rel.endswith(".pyc"):
            continue

        if "/backup/" in rel:
            continue

        if "/backups/" in rel:
            continue

        if "app.backup_" in rel:
            continue

        score = 0

        name = str(f.relative_to(ROOT)).lower()

        for token in tokens:
            if token in name:
                score += 10

        try:
            content = f.read_text(encoding="utf-8").lower()
        except Exception:
            continue

        for token in tokens:
            score += content.count(token)

        if score:
            scored.append((score, str(f.relative_to(ROOT))))

    scored.sort(reverse=True)

    return {
        "ok": True,
        "matches": [p for _, p in scored[:20]],
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


from pathlib import Path
import shutil


def apply_file(path: str, content: str):

    p = _resolve(path)

    backup = p.with_suffix(
        p.suffix + ".bak"
    )

    shutil.copy2(p, backup)

    p.write_text(
        content,
        encoding="utf-8"
    )

    result = compile()

    if not result["ok"]:

        shutil.copy2(
            backup,
            p
        )

        return {
            "ok": False,
            "rollback": True,
            "message": "Falha na compilação. Backup restaurado.",
            "compile": result,
        }

    return {
        "ok": True,
        "backup": str(backup),
        "compile": result,
    }

