from __future__ import annotations

from typing import Any, Callable


def handle_git_op(req: Any, run_cmd: Callable[..., dict[str, Any]]) -> dict[str, Any] | None:
    op = req.operation
    cwd = req.path or "/opt/agente-divina-v2"

    if op in {"git_status", "project_git_status"}:
        return {"ok": True, "result": run_cmd("git status --short", cwd=cwd)}

    if op in {"git_diff", "project_git_diff"}:
        return {"ok": True, "result": run_cmd("git diff -- .", cwd=cwd)}

    if op in {"project_commit", "git_commit"}:
        args = req.args or {}
        message = args.get("message") or req.content or "chore: atualização operacional"
        files = args.get("files") or "."
        return {"ok": True, "result": run_cmd(f"git add {files} && git commit -m {message!r}", cwd=cwd)}

    if op in {"project_push", "git_push"}:
        branch = (req.args or {}).get("branch") or "main"
        return {"ok": True, "result": run_cmd(f"git push origin {branch}", cwd=cwd)}

    return None
