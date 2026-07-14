from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import HTTPException


def handle_project_op(
    req: Any,
    safe_path: Callable[[str], Path],
    run_cmd: Callable[..., dict[str, Any]],
) -> dict[str, Any] | None:
    """Operações de projeto para o Agente Divina.

    Retorna None quando a operação não pertence a este módulo.
    """
    op = req.operation

    if op == "project_search":
        root = safe_path(req.path or "/opt/agente-divina-v2")
        term = req.find or ""
        if not term:
            raise HTTPException(400, "find obrigatório")
        found: list[str] = []
        for f in root.rglob("*"):
            if len(found) >= (req.limit or 200):
                break
            if f.is_file():
                try:
                    txt = f.read_text(errors="ignore")
                    if term in txt:
                        found.append(str(f))
                except Exception:
                    pass
        return {"ok": True, "term": term, "count": len(found), "found": found}

    if op == "project_replace_all":
        root = safe_path(req.path or "/opt/agente-divina-v2")
        if not req.find:
            raise HTTPException(400, "find obrigatório")
        changed = []
        for f in root.rglob("*"):
            if len(changed) >= (req.limit or 200):
                break
            if not f.is_file():
                continue
            try:
                txt = f.read_text(errors="ignore")
            except Exception:
                continue
            if req.find in txt:
                backup = f.with_suffix(f.suffix + f".bak-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
                backup.write_text(txt)
                f.write_text(txt.replace(req.find, req.replace or ""))
                changed.append({"path": str(f), "backup": str(backup)})
        return {"ok": True, "changed_count": len(changed), "changed": changed}

    if op == "project_build":
        cwd = req.path or "/opt/agente-divina-v2"
        return {"ok": True, "result": run_cmd("npm run build", cwd=cwd)}

    if op == "project_test":
        cwd = req.path or "/opt/agente-divina-v2"
        cmd = req.command or "npm test -- --watch=false"
        return {"ok": True, "result": run_cmd(cmd, cwd=cwd)}

    if op == "project_git_status":
        cwd = req.path or "/opt/agente-divina-v2"
        return {"ok": True, "result": run_cmd("git status --short", cwd=cwd)}

    if op == "project_git_diff":
        cwd = req.path or "/opt/agente-divina-v2"
        return {"ok": True, "result": run_cmd("git diff -- .", cwd=cwd)}

    if op == "project_commit":
        cwd = req.path or "/opt/agente-divina-v2"
        args = req.args or {}
        message = args.get("message") or req.content or "chore: atualização operacional"
        files = args.get("files") or "."
        return {"ok": True, "result": run_cmd(f"git add {files} && git commit -m {message!r}", cwd=cwd)}

    if op == "project_push":
        cwd = req.path or "/opt/agente-divina-v2"
        branch = (req.args or {}).get("branch") or "main"
        return {"ok": True, "result": run_cmd(f"git push origin {branch}", cwd=cwd)}

    if op == "project_healthcheck":
        url = (req.args or {}).get("url") or "https://grupo-divina-dashboard.vercel.app/auth/login"
        return {"ok": True, "result": run_cmd(f"curl -s -I {url} | head -30")}

    if op == "project_clean_backups":
        root = safe_path(req.path or "/opt/agente-divina-v2/app")
        deleted = []
        for f in root.rglob("*"):
            if f.is_file() and (".bak-" in f.name or ".bak_" in f.name):
                f.unlink()
                deleted.append(str(f))
        return {"ok": True, "deleted_count": len(deleted), "deleted": deleted[: req.limit or 200]}

    if op == "execute_plan":
        args = req.args or {}
        plan = args.get("plan") or req.content or ""
        cwd = args.get("cwd") or "/opt/agente-divina-v2"
        steps = []

        if plan != "frontend_validate_commit_push":
            raise HTTPException(400, f"plano não suportado: {plan}")

        steps.append({"step": "status_before", "result": run_cmd("git status --short", cwd=cwd)})
        steps.append({"step": "build", "result": run_cmd("npm run build", cwd=cwd)})
        if steps[-1]["result"]["returncode"] != 0:
            return {"ok": False, "plan": plan, "stopped_at": "build", "steps": steps}

        msg = args.get("message") or "chore: atualização operacional"
        files = args.get("files") or "."
        steps.append({"step": "commit", "result": run_cmd(f"git add {files} && git commit -m {msg!r}", cwd=cwd)})
        if steps[-1]["result"]["returncode"] not in (0, 1):
            return {"ok": False, "plan": plan, "stopped_at": "commit", "steps": steps}

        steps.append({"step": "push", "result": run_cmd("git push origin main", cwd=cwd)})
        steps.append({"step": "healthcheck", "result": run_cmd("curl -s -I https://grupo-divina-dashboard.vercel.app/auth/login | head -30")})
        return {"ok": steps[-2]["result"]["returncode"] == 0, "plan": plan, "steps": steps}

    return None
