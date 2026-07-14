from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import authorization_header, bearerAuth, verify_token
from app.config import (
    APP_CWD,
    DASHBOARD_CWD,
    FORNECEDORES_CWD,
    load_api_config,
    load_supabase_config,
)
from app.models import (
    AdminExecRequest,
    AdminGitRequest,
    AdminListFilesRequest,
    AdminPatchFileRequest,
    AdminReadFileRequest,
    AdminRestartServiceRequest,
    AdminSupabaseQueryRequest,
    AdminWriteFileRequest,
    ShellRequest,
)
from app.routes.runtime import runtime
from app.routes.status import health
from app.utils import run_cmd


router = APIRouter()


@router.post("/admin/shell")
def admin_shell(
    payload: ShellRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    config_api = load_api_config()
    config_supabase = load_supabase_config()

    api_token = config_api.get("AGENTE_API_TOKEN")
    admin_token = config_supabase.get("AGENTE_ADMIN_TOKEN")
    authorization = authorization_header(credentials)

    if authorization not in [f"Bearer {api_token}", f"Bearer {admin_token}"]:
        raise HTTPException(status_code=401, detail="Token inválido")

    cmd = payload.cmd.strip()

    proibidos = [
        "rm -rf /",
        "mkfs",
        "shutdown",
        "reboot",
        "passwd",
        "useradd",
        "deluser",
        "chmod 777",
        ":(){",
        "dd if=",
    ]

    for item in proibidos:
        if item in cmd:
            raise HTTPException(status_code=403, detail=f"Comando bloqueado: {item}")

    log_line = f"{datetime.utcnow().isoformat()} | {cmd}\n"
    with open("/opt/agente-divina/logs/admin_shell.log", "a") as f:
        f.write(log_line)

    return run_cmd(cmd)


@router.get("/admin/status-real")
def admin_status_real(
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    checks = {
        "api": "ok",
        "runtime": runtime(),
        "health": health(),
    }

    return {
        "ok": True,
        "servico": "agente-divina",
        "modo": "servidor-real",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/admin/agente-mestre-real")
def admin_agente_mestre_real(
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    try:
        resp = requests.get("http://127.0.0.1:8020/health", timeout=10)
        try:
            data = resp.json()
        except Exception:
            data = resp.text

        return {
            "ok": resp.status_code == 200,
            "servico": "agente-mestre",
            "modo": "servidor-real",
            "status_http": resp.status_code,
            "resposta": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "ok": False,
            "servico": "agente-mestre",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/admin/exec")
def admin_exec(
    payload: AdminExecRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    cmd = str(payload.cmd).strip()
    cwd = str(payload.cwd).strip()

    allowed_cwd = [
        DASHBOARD_CWD,
        "/opt/agente-divina",
        FORNECEDORES_CWD,
    ]

    if cwd not in allowed_cwd:
        return {"ok": False, "erro": "cwd não permitido", "cwd": cwd}

    if not cmd:
        return {"ok": False, "erro": "cmd vazio"}

    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    return {
        "ok": proc.returncode == 0,
        "cmd": cmd,
        "cwd": cwd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


@router.post("/admin/read-file")
def admin_read_file(
    payload: AdminReadFileRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    path = Path(str(payload.path)).resolve()

    allowed_roots = [
        Path(DASHBOARD_CWD).resolve(),
        Path("/opt/agente-divina").resolve(),
        Path(FORNECEDORES_CWD).resolve(),
    ]

    if not any(str(path).startswith(str(root)) for root in allowed_roots):
        return {"ok": False, "erro": "Arquivo fora dos diretórios permitidos", "path": str(path)}

    if not path.exists() or not path.is_file():
        return {"ok": False, "erro": "Arquivo não encontrado", "path": str(path)}

    return {
        "ok": True,
        "path": str(path),
        "content": path.read_text(encoding="utf-8", errors="replace"),
    }


@router.post("/admin/write-file")
def admin_write_file(
    payload: AdminWriteFileRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    path = Path(str(payload.path)).resolve()
    content = str(payload.content)

    allowed_roots = [
        Path(DASHBOARD_CWD).resolve(),
        Path("/opt/agente-divina").resolve(),
        Path(FORNECEDORES_CWD).resolve(),
    ]

    if not any(str(path).startswith(str(root)) for root in allowed_roots):
        return {"ok": False, "erro": "Arquivo fora dos diretórios permitidos", "path": str(path)}

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "path": str(path),
        "bytes": len(content.encode("utf-8")),
    }


@router.post("/admin/list-files")
def admin_list_files(
    payload: AdminListFilesRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    base = Path(str(payload.path)).resolve()
    pattern = str(payload.pattern)
    max_items = int(payload.max_items)

    allowed_roots = [
        Path(DASHBOARD_CWD).resolve(),
        Path("/opt/agente-divina").resolve(),
        Path(FORNECEDORES_CWD).resolve(),
    ]

    if not any(str(base).startswith(str(root)) for root in allowed_roots):
        return {"ok": False, "erro": "Diretório fora dos permitidos", "path": str(base)}

    if not base.exists() or not base.is_dir():
        return {"ok": False, "erro": "Diretório não encontrado", "path": str(base)}

    items = []
    for p in base.rglob(pattern):
        if len(items) >= max_items:
            break
        items.append({
            "path": str(p),
            "type": "dir" if p.is_dir() else "file",
            "size": p.stat().st_size if p.is_file() else None,
        })

    return {
        "ok": True,
        "base": str(base),
        "pattern": pattern,
        "count": len(items),
        "items": items,
    }


@router.post("/admin/git")
def admin_git(
    payload: AdminGitRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    action = str(payload.action).strip()
    message = str(payload.message).strip()
    cwd = str(payload.cwd).strip()

    allowed_cwd = [
        DASHBOARD_CWD,
        "/opt/agente-divina",
        FORNECEDORES_CWD,
    ]

    if cwd not in allowed_cwd:
        return {"ok": False, "erro": "cwd não permitido", "cwd": cwd}

    comandos = {
        "status": "git status",
        "pull": "git pull --rebase origin main",
        "diff": "git diff",
        "log": "git log --oneline -10",
        "push": "git push origin main",
    }

    if action == "commit":
        if not message:
            return {"ok": False, "erro": "message obrigatório para commit"}
        cmd = f'git add . && git commit -m "{message}"'
    elif action == "sync":
        if not message:
            return {"ok": False, "erro": "message obrigatório para sync"}
        cmd = f'git pull --rebase origin main && git add . && git commit -m "{message}" && git push origin main'
    elif action in comandos:
        cmd = comandos[action]
    else:
        return {"ok": False, "erro": "action inválida", "actions": ["status", "pull", "diff", "log", "commit", "push", "sync"]}

    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=180,
    )

    return {
        "ok": proc.returncode == 0,
        "action": action,
        "cmd": cmd,
        "cwd": cwd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


@router.post("/admin/supabase-query")
def admin_supabase_query(
    payload: AdminSupabaseQueryRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    import os
    import psycopg2
    import psycopg2.extras

    sql = str(payload.sql).strip()
    params = payload.params

    if not sql.lower().startswith("select"):
        return {"ok": False, "erro": "Apenas SELECT permitido neste endpoint"}

    proibidos = ["insert ", "update ", "delete ", "drop ", "alter ", "truncate ", "create ", "grant ", "revoke "]
    if any(p in sql.lower() for p in proibidos):
        return {"ok": False, "erro": "Comando SQL não permitido"}

    conn_str = os.getenv("SUPABASE_DB_URL")
    if not conn_str:
        return {"ok": False, "erro": "SUPABASE_DB_URL não configurado no ambiente do agente"}

    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        return {
            "ok": True,
            "count": len(rows),
            "rows": rows[:500],
        }
    except Exception as e:
        return {"ok": False, "erro": str(e)}


@router.post("/admin/patch-file")
def admin_patch_file(
    payload: AdminPatchFileRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    import shutil
    import time

    allowed_roots = [
        Path(APP_CWD).resolve(),
        Path("/opt/agente-divina/config").resolve(),
        Path(DASHBOARD_CWD).resolve(),
        Path(FORNECEDORES_CWD).resolve(),
    ]

    file_path = Path(str(payload.file)).resolve()
    search = payload.search
    replace = payload.replace
    compile_python = bool(payload.compile_python)

    if not str(file_path):
        return {"ok": False, "erro": "file obrigatório"}
    if search is None or replace is None:
        return {"ok": False, "erro": "search e replace são obrigatórios"}
    if not any(str(file_path).startswith(str(root)) for root in allowed_roots):
        return {"ok": False, "erro": "arquivo fora dos diretórios permitidos", "file": str(file_path)}
    if not file_path.exists() or not file_path.is_file():
        return {"ok": False, "erro": "arquivo não encontrado", "file": str(file_path)}

    text = file_path.read_text()
    occurrences = text.count(str(search))
    if occurrences == 0:
        return {"ok": False, "erro": "trecho search não encontrado", "file": str(file_path)}

    backup = file_path.with_name(file_path.name + f".bak_patch_{int(time.time())}")
    shutil.copy2(file_path, backup)
    new_text = text.replace(str(search), str(replace), 1)
    file_path.write_text(new_text)

    compile_result = None
    if compile_python and file_path.suffix == ".py":
        proc = subprocess.run(
            ["/opt/agente-divina/app/venv/bin/python", "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        compile_result = {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
        }
        if proc.returncode != 0:
            shutil.copy2(backup, file_path)
            return {
                "ok": False,
                "erro": "compilação falhou; arquivo restaurado do backup",
                "backup": str(backup),
                "compile": compile_result,
            }

    return {
        "ok": True,
        "file": str(file_path),
        "backup": str(backup),
        "occurrences_before": occurrences,
        "replaced": 1,
        "compile": compile_result,
    }


@router.post("/admin/restart-service")
def admin_restart_service(
    payload: AdminRestartServiceRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    import time

    service = str(payload.service)
    allowed = {
    "agente-divina-api.service",
    "agente-divina-v2.service",
    "nginx.service",
    "nginx",
}
    if service not in allowed:
        return {"ok": False, "erro": "serviço não permitido", "allowed": sorted(allowed)}

    proc = subprocess.run(
        ["systemctl", "restart", service],
        capture_output=True,
        text=True,
        timeout=120,
    )
    time.sleep(2)
    status = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True,
        timeout=20,
    )

    return {
        "ok": proc.returncode == 0 and status.stdout.strip() == "active",
        "service": service,
        "restart_exit_code": proc.returncode,
        "restart_stdout": proc.stdout,
        "restart_stderr": proc.stderr,
        "status": status.stdout.strip(),
        "status_stderr": status.stderr,
    }

