from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path
from typing import Any, Callable

from fastapi import HTTPException

FRONTEND_ROOT = Path("/opt/agente-divina-v2").resolve()
AUDIT_DIR = Path("/opt/agente-divina/logs/frontend_execute_plan")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_ROOT = Path(__file__).resolve().parent / "frontend_templates"


def _now() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def _safe_frontend_path(path: str | None) -> Path:
    if not path:
        raise HTTPException(400, "path obrigatório")
    p = Path(path)
    if not p.is_absolute():
        p = FRONTEND_ROOT / p
    p = p.resolve()
    if not str(p).startswith(str(FRONTEND_ROOT)):
        raise HTTPException(403, f"path fora do frontend: {p}")
    return p


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + f".bak-frontend-{_now()}")
    if path.is_dir():
        shutil.copytree(path, backup)
    else:
        backup.write_bytes(path.read_bytes())
    return backup


def _restore(backups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    restored: list[dict[str, Any]] = []
    for item in reversed(backups):
        target = Path(item["target"])
        backup = item.get("backup")
        existed = bool(item.get("existed"))
        try:
            if existed and backup:
                src = Path(backup)
                if target.exists():
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                if src.is_dir():
                    shutil.copytree(src, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
                restored.append(item)
            elif not existed and target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                restored.append(item)
        except Exception as exc:
            restored.append({"target": str(target), "backup": backup, "restore_error": str(exc)})
    return restored


def _write_audit(plan: str, report: dict[str, Any]) -> str:
    path = AUDIT_DIR / f"{plan}-{_now()}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(path)


def _run(run_cmd: Callable[..., dict[str, Any]], cmd: str, cwd: str | Path = FRONTEND_ROOT) -> dict[str, Any]:
    return run_cmd(cmd, cwd=str(cwd))


def _preset_steps(plan: str) -> list[dict[str, Any]]:
    if plan in {"frontend_validate", "validar_frontend"}:
        return [
            {"action": "build"},
            {"action": "smoke_test"},
            {"action": "browser_flow", "flow": "login", "args": {"login": "jrdepinho", "password": "12345678", "timeout": 20000}},
            {"action": "browser_flow", "flow": "abrir_erp", "args": {"timeout": 20000}},
        ]
    if plan in {"frontend_status", "status_frontend"}:
        return [
            {"action": "git_status"},
            {"action": "tree", "path": ".", "limit": 80},
        ]
    return []



def _render_template(rel: str, replacements: dict[str, str] | None = None) -> str:
    content = (TEMPLATE_ROOT / rel).read_text(encoding="utf-8")
    for key, value in (replacements or {}).items():
        content = content.replace("{{" + key + "}}", value)
    return content


def _generate_security_module_files() -> dict[str, str]:
    return {
        "app/erp/seguranca/page.jsx": _render_template("security/dashboard.jsx"),
        "app/erp/seguranca/usuarios/page.jsx": _render_template("security/users.jsx"),
        "app/erp/seguranca/perfis/page.jsx": _render_template("security/placeholder.jsx", {"TITLE": "Perfis", "SUBTITLE": "Gestão de perfis de acesso"}),
        "app/erp/seguranca/permissoes/page.jsx": _render_template("security/placeholder.jsx", {"TITLE": "Permissões", "SUBTITLE": "Matriz de permissões por módulo"}),
        "app/erp/seguranca/empresas/page.jsx": _render_template("security/placeholder.jsx", {"TITLE": "Empresas", "SUBTITLE": "Acessos por empresa e unidade"}),
        "app/erp/seguranca/auditoria/page.jsx": _render_template("security/placeholder.jsx", {"TITLE": "Auditoria de Segurança", "SUBTITLE": "Histórico de alterações de usuários e acessos"}),
    }

def handle_frontend_project_op(req: Any, run_cmd: Callable[..., dict[str, Any]]) -> dict[str, Any] | None:
    op = req.operation
    if not str(op).startswith("frontend_"):
        return None

    args = req.args or {}

    if op in {"frontend_project_tree", "frontend_tree"}:
        root = _safe_frontend_path(req.path or args.get("path") or ".")
        limit = int(req.limit or args.get("limit") or 200)
        recursive = bool(req.recursive or args.get("recursive", False))
        iterator = root.rglob("*") if recursive else root.iterdir()
        items = []
        for item in list(iterator)[:limit]:
            rel = item.relative_to(FRONTEND_ROOT)
            items.append({"path": str(rel), "type": "dir" if item.is_dir() else "file"})
        return {"ok": True, "root": str(FRONTEND_ROOT), "items": items}

    if op in {"frontend_project_read", "frontend_read"}:
        p = _safe_frontend_path(req.path or args.get("path"))
        return {"ok": True, "path": str(p.relative_to(FRONTEND_ROOT)), "content": p.read_text(errors="replace")}

    if op in {"frontend_project_write", "frontend_write", "frontend_project_create_file"}:
        p = _safe_frontend_path(req.path or args.get("path"))
        existed = p.exists()
        backup = _backup(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(req.content if req.content is not None else str(args.get("content") or ""), encoding="utf-8")
        return {"ok": True, "path": str(p.relative_to(FRONTEND_ROOT)), "backup": str(backup) if backup else None, "existed": existed}

    if op in {"frontend_project_mkdir", "frontend_mkdir"}:
        p = _safe_frontend_path(req.path or args.get("path"))
        p.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "path": str(p.relative_to(FRONTEND_ROOT))}

    if op in {"frontend_project_patch", "frontend_patch"}:
        p = _safe_frontend_path(req.path or args.get("path"))
        find = req.find if req.find is not None else args.get("find")
        replace = req.replace if req.replace is not None else args.get("replace", "")
        if not find:
            raise HTTPException(400, "find obrigatório")
        text = p.read_text(errors="replace")
        if find not in text:
            raise HTTPException(404, "trecho find não encontrado")
        backup = _backup(p)
        p.write_text(text.replace(str(find), str(replace), int(args.get("count") or 1)), encoding="utf-8")
        return {"ok": True, "path": str(p.relative_to(FRONTEND_ROOT)), "backup": str(backup) if backup else None}

    if op in {"frontend_project_search", "frontend_search"}:
        root = _safe_frontend_path(req.path or args.get("path") or ".")
        term = req.find or args.get("find") or ""
        if not term:
            raise HTTPException(400, "find obrigatório")
        limit = int(req.limit or args.get("limit") or 200)
        found = []
        for f in root.rglob("*"):
            if len(found) >= limit:
                break
            if f.is_file():
                try:
                    if str(term) in f.read_text(errors="ignore"):
                        found.append(str(f.relative_to(FRONTEND_ROOT)))
                except Exception:
                    pass
        return {"ok": True, "count": len(found), "found": found}

    if op in {"frontend_project_delete", "frontend_delete"}:
        p = _safe_frontend_path(req.path or args.get("path"))
        backup = _backup(p)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
        return {"ok": True, "path": str(p.relative_to(FRONTEND_ROOT)), "backup": str(backup) if backup else None}

    if op in {"frontend_project_build", "frontend_build"}:
        return {"ok": True, "result": _run(run_cmd, "npm run build")}

    if op in {"frontend_project_lint", "frontend_lint"}:
        return {"ok": True, "result": _run(run_cmd, "npm run lint")}

    if op in {"frontend_project_git_status", "frontend_git_status"}:
        return {"ok": True, "result": _run(run_cmd, "git status --short")}

    if op in {"frontend_project_git_diff", "frontend_git_diff"}:
        return {"ok": True, "result": _run(run_cmd, "git diff -- .")}

    if op in {"frontend_project_commit", "frontend_commit"}:
        message = args.get("message") or req.content or "chore: atualização frontend"
        files = args.get("files") or "."
        return {"ok": True, "result": _run(run_cmd, f"git add {files} && git commit -m {message!r}")}

    if op in {"frontend_project_push", "frontend_push"}:
        branch = args.get("branch") or "main"
        return {"ok": True, "result": _run(run_cmd, f"git push origin {branch}")}

    if op in {"frontend_project_validate", "frontend_validate"}:
        steps = [
            {"name": "build", "result": _run(run_cmd, "npm run build")},
        ]
        ok = all(s["result"].get("returncode") == 0 for s in steps)
        return {"ok": ok, "steps": steps}

    if op in {"frontend_generate_module", "frontend_project_generate_module"}:
        module = str(args.get("module") or req.content or "").strip().lower()
        if module not in {"seguranca", "security"}:
            raise HTTPException(400, f"módulo frontend não suportado: {module}")
        files = _generate_security_module_files()
        written: list[str] = []
        backups: list[dict[str, Any]] = []
        for rel, content in files.items():
            p = _safe_frontend_path(rel)
            existed = p.exists()
            backup = _backup(p)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            written.append(rel)
            backups.append({"target": str(p), "backup": str(backup) if backup else None, "existed": existed})
        sidebar = _safe_frontend_path("components/erp/ErpSidebar.jsx")
        sidebar_text = sidebar.read_text(errors="replace")
        if '["Segurança", "/erp/seguranca"]' not in sidebar_text:
            backup = _backup(sidebar)
            marker = '  ["Relatorios", "/erp/relatorios"],\n'
            addition = '  ["Segurança", "/erp/seguranca"],\n  ["  Dashboard Segurança", "/erp/seguranca"],\n  ["  Usuários", "/erp/seguranca/usuarios"],\n  ["  Perfis", "/erp/seguranca/perfis"],\n  ["  Permissões", "/erp/seguranca/permissoes"],\n  ["  Empresas e Unidades", "/erp/seguranca/empresas"],\n  ["  Auditoria Segurança", "/erp/seguranca/auditoria"],\n'
            if marker not in sidebar_text:
                raise HTTPException(404, "marcador do sidebar não encontrado")
            sidebar.write_text(sidebar_text.replace(marker, addition + marker), encoding="utf-8")
            backups.append({"target": str(sidebar), "backup": str(backup) if backup else None, "existed": True})
        return {"ok": True, "module": module, "written": written, "backups": backups}

    if op == "frontend_execute_plan":
        plan = str(args.get("plan") or req.content or "frontend_custom")
        steps = args.get("steps") or _preset_steps(plan)
        if not isinstance(steps, list):
            raise HTTPException(400, "args.steps deve ser uma lista")
        backups: list[dict[str, Any]] = []
        report_steps: list[dict[str, Any]] = []
        rollback_on_error = bool(args.get("rollback_on_error", True))
        stop_on_error = bool(args.get("stop_on_error", True))

        def finish(ok: bool, stopped_at: str | None = None) -> dict[str, Any]:
            report = {"ok": ok, "plan": plan, "stopped_at": stopped_at, "steps": report_steps, "backups": backups}
            report["audit_path"] = _write_audit(plan, report)
            return report

        for index, step in enumerate(steps, start=1):
            action = str(step.get("action") or "")
            item: dict[str, Any] = {"index": index, "action": action, "ok": True}
            try:
                if action == "write_file":
                    p = _safe_frontend_path(step.get("path"))
                    existed = p.exists()
                    backup = _backup(p)
                    backups.append({"target": str(p), "backup": str(backup) if backup else None, "existed": existed})
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(str(step.get("content") or ""), encoding="utf-8")
                    item.update({"path": str(p.relative_to(FRONTEND_ROOT)), "backup": str(backup) if backup else None})
                elif action == "patch_file":
                    p = _safe_frontend_path(step.get("path"))
                    text = p.read_text(errors="replace")
                    find = str(step.get("find") or "")
                    if not find or find not in text:
                        raise HTTPException(404, "trecho find não encontrado")
                    backup = _backup(p)
                    backups.append({"target": str(p), "backup": str(backup) if backup else None, "existed": True})
                    p.write_text(text.replace(find, str(step.get("replace") or ""), int(step.get("count") or 1)), encoding="utf-8")
                    item.update({"path": str(p.relative_to(FRONTEND_ROOT)), "backup": str(backup) if backup else None})
                elif action == "mkdir":
                    p = _safe_frontend_path(step.get("path"))
                    p.mkdir(parents=True, exist_ok=True)
                    item["path"] = str(p.relative_to(FRONTEND_ROOT))
                elif action == "build":
                    result = _run(run_cmd, str(step.get("command") or "npm run build"))
                    item["result"] = result
                    item["ok"] = result.get("returncode") == 0
                elif action == "lint":
                    result = _run(run_cmd, str(step.get("command") or "npm run lint"))
                    item["result"] = result
                    item["ok"] = result.get("returncode") == 0
                elif action == "git_status":
                    item["result"] = _run(run_cmd, "git status --short")
                elif action == "git_diff":
                    item["result"] = _run(run_cmd, "git diff -- .")
                elif action == "commit":
                    message = step.get("message") or "chore: atualização frontend"
                    files = step.get("files") or "."
                    result = _run(run_cmd, f"git add {files} && git commit -m {message!r}")
                    item["result"] = result
                    item["ok"] = result.get("returncode") in (0, 1)
                elif action == "push":
                    branch = step.get("branch") or "main"
                    result = _run(run_cmd, f"git push origin {branch}")
                    item["result"] = result
                    item["ok"] = result.get("returncode") == 0
                elif action == "smoke_test":
                    payload = json.dumps({"operation": "smoke_test", "args": step.get("args") or {}})
                    cmd = f"TOKEN=$(grep AGENTE_ADMIN_TOKEN /opt/agente-divina/config/supabase.env | cut -d= -f2-); curl -s -X POST http://127.0.0.1:8000/admin/full-access -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d {payload!r}"
                    result = _run(run_cmd, cmd, cwd="/opt/agente-divina-v2")
                    item["result"] = result
                    item["ok"] = result.get("returncode") == 0 and '"ok":true' in result.get("stdout", "")
                elif action == "browser_flow":
                    args2 = dict(step.get("args") or {})
                    if step.get("flow"):
                        args2["flow"] = step.get("flow")
                    payload = json.dumps({"operation": "browser_flow", "args": args2})
                    cmd = f"TOKEN=$(grep AGENTE_ADMIN_TOKEN /opt/agente-divina/config/supabase.env | cut -d= -f2-); curl -s -X POST http://127.0.0.1:8000/admin/full-access -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d {payload!r}"
                    result = _run(run_cmd, cmd, cwd="/opt/agente-divina-v2")
                    item["result"] = result
                    item["ok"] = result.get("returncode") == 0 and '"ok":true' in result.get("stdout", "")
                else:
                    raise HTTPException(400, f"ação frontend não suportada: {action}")
            except Exception as exc:
                item["ok"] = False
                item["error"] = str(exc)
            report_steps.append(item)
            if not item.get("ok") and stop_on_error:
                if rollback_on_error:
                    item["restored"] = _restore(backups)
                return finish(False, action)
        return finish(all(s.get("ok") for s in report_steps))

    return None
