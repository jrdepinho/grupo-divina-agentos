from __future__ import annotations

import requests
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import bearerAuth, verify_admin_token, verify_token
from app.config import load_supabase_config
from app.models import SQLRequest
from app.utils import run_cmd


router = APIRouter()


@router.post("/supabase/teste")
def supabase_teste(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    verify_token(credentials)
    return run_cmd("source venv/bin/activate && agente-divina supabase")


@router.post("/supabase/sql")
def supabase_sql(
    payload: SQLRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_token(credentials)

    config_supabase = load_supabase_config()
    url = config_supabase.get("SUPABASE_URL")
    key = config_supabase.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase não configurado")

    sql_limpo = payload.sql.strip().rstrip(";").strip()
    sql_lower = sql_limpo.lower()

    # SELECT retorna dados; demais comandos executam alteração/DDL.
    rpc = "execute_select" if sql_lower.startswith("select") else "execute_sql"

    resp = requests.post(
        f"{url}/rest/v1/rpc/{rpc}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={"query": sql_limpo},
        timeout=60,
    )

    try:
        parsed = resp.json()
    except Exception:
        parsed = resp.text

    return {
        "ok": resp.status_code in (200, 201, 204),
        "rpc": rpc,
        "status_code": resp.status_code,
        "response": parsed,
    }


@router.post("/supabase/admin/sql")
def supabase_admin_sql(
    payload: SQLRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    config = verify_admin_token(credentials)

    url = config.get("SUPABASE_URL")
    key = config.get("SUPABASE_SERVICE_ROLE_KEY")

    sql_limpo = payload.sql.strip().rstrip(";").strip()
    sql_lower = sql_limpo.lower()

    rpc = "execute_select" if sql_lower.startswith("select") else "execute_sql"

    resp = requests.post(
        f"{url}/rest/v1/rpc/{rpc}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={"query": sql_limpo},
        timeout=120,
    )

    try:
        parsed = resp.json()
    except Exception:
        parsed = resp.text

    return {
        "ok": resp.status_code in (200, 201, 204),
        "status": resp.status_code,
        "response": parsed,
    }

