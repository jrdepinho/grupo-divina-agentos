from __future__ import annotations

from collections import Counter
from typing import Any, Callable


def _run(run_cmd: Callable[..., dict[str, Any]], name: str, command: str, cwd: str):
    result = run_cmd(command, cwd=cwd)
    return {
        "name": name,
        "ok": result.get("returncode") == 0,
        "returncode": result.get("returncode"),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
    }


def _openapi_operation_ids_unique() -> dict[str, Any]:
    try:
        from app.main import app

        schema = app.openapi()
        operation_ids: list[str] = []
        for _path, methods in schema.get("paths", {}).items():
            for _method, spec in methods.items():
                if isinstance(spec, dict) and spec.get("operationId"):
                    operation_ids.append(spec["operationId"])

        duplicates = {
            op_id: count
            for op_id, count in Counter(operation_ids).items()
            if count > 1
        }

        return {
            "name": "openapi_operation_ids_unique",
            "ok": not duplicates,
            "total": len(operation_ids),
            "unique": len(set(operation_ids)),
            "duplicates": duplicates,
        }
    except Exception as exc:
        return {
            "name": "openapi_operation_ids_unique",
            "ok": False,
            "error": str(exc),
        }


def handle_smoke_op(req: Any, run_cmd: Callable[..., dict[str, Any]]):
    if req.operation not in {"smoke_test", "health_suite", "project_smoke_test"}:
        return None

    args = req.args or {}
    backend_root = args.get("backend_root") or "/opt/agente-divina-v2"
    frontend_root = args.get("frontend_root") or "/opt/agente-divina-v2"
    public_url = args.get("public_url") or "https://grupo-divina-dashboard.vercel.app/auth/login"
    run_frontend_build = bool(args.get("run_frontend_build", False))
    run_openapi_audit = bool(args.get("run_openapi_audit", True))

    steps: list[dict[str, Any]] = []

    steps.append(_run(
        run_cmd,
        "python_compile_backend",
        "python3 -m py_compile app/main.py app/routes/admin_full_access.py app/routes/compact.py app/admin_ops/*.py",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "backend_service_active",
        "systemctl is-active agente-divina-v2.service",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "backend_openapi_local",
        "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/openapi.json | grep -q '^200$'",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "admin_full_access_list",
        "TOKEN=$(grep AGENTE_ADMIN_TOKEN /opt/agente-divina/config/supabase.env | cut -d= -f2-); curl -s -X POST http://127.0.0.1:8000/admin/full-access -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d '{\"operation\":\"list_dir\",\"path\":\"/opt/agente-divina-v2/app/admin_ops\",\"limit\":3}' | grep -q '\"ok\":true'",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "admin_service_status",
        "TOKEN=$(grep AGENTE_ADMIN_TOKEN /opt/agente-divina/config/supabase.env | cut -d= -f2-); curl -s -X POST http://127.0.0.1:8000/admin/full-access -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d '{\"operation\":\"service_status\",\"service\":\"agente-divina-v2.service\"}' | grep -q '\"ok\":true'",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "admin_git_status_frontend",
        "TOKEN=$(grep AGENTE_ADMIN_TOKEN /opt/agente-divina/config/supabase.env | cut -d= -f2-); curl -s -X POST http://127.0.0.1:8000/admin/full-access -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d '{\"operation\":\"project_git_status\",\"path\":\"/opt/agente-divina-v2\"}' | grep -q '\"ok\":true'",
        backend_root,
    ))

    steps.append(_run(
        run_cmd,
        "frontend_login_http",
        f"curl -s -I {public_url} | head -20 | grep -q '200'",
        frontend_root,
    ))

    steps.append(_run(
        run_cmd,
        "frontend_erp_http",
        "curl -s -I https://grupo-divina-dashboard.vercel.app/erp | head -20 | grep -E -q '200|307|308'",
        frontend_root,
    ))

    steps.append(_run(
        run_cmd,
        "frontend_resolve_login",
        "curl -s -X POST https://grupo-divina-dashboard.vercel.app/api/auth/resolve-login -H 'Content-Type: application/json' -d '{\"login\":\"jrdepinho\"}' | grep -q 'jrdepinho@divinahomepy.com'",
        frontend_root,
    ))

    if run_frontend_build:
        steps.append(_run(run_cmd, "frontend_build", "npm run build", frontend_root))

    if run_openapi_audit:
        steps.append(_openapi_operation_ids_unique())

    ok = all(step.get("ok") for step in steps)
    return {
        "ok": ok,
        "summary": {
            "total": len(steps),
            "passed": sum(1 for s in steps if s.get("ok")),
            "failed": sum(1 for s in steps if not s.get("ok")),
        },
        "steps": steps,
    }
