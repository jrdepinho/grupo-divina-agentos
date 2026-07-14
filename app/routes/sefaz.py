from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import authorization_header, bearerAuth, verify_token
from app.utils import read_status_sefaz_json, run_cmd


router = APIRouter()


@router.get("/nsu")
def nsu(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    verify_token(credentials)
    with open("/opt/agente-divina/config/hogar_nsu.txt") as f:
        hogar = f.read().strip()
    with open("/opt/agente-divina/config/ttf_nsu.txt") as f:
        ttf = f.read().strip()
    return {"hogar": hogar, "ttf": ttf}


@router.post("/processar-xml")
def processar_xml(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    verify_token(credentials)
    return run_cmd("source venv/bin/activate && agente-divina processar-xml")


@router.post("/sefaz/hogar")
def sefaz_hogar(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    verify_token(credentials)
    return run_cmd("source venv/bin/activate && agente-divina sefaz-hogar")


@router.post("/sefaz/ttf")
def sefaz_ttf(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    verify_token(credentials)
    return run_cmd("source venv/bin/activate && agente-divina sefaz-ttf")


@router.get("/api/status-sefaz")
def status_sefaz(credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth)):
    token_esperado = os.getenv("STATUS_SEFAZ_TOKEN")

    if not token_esperado:
        raise HTTPException(
            status_code=500,
            detail={"ok": False, "error": "STATUS_SEFAZ_TOKEN_nao_configurado"},
        )

    authorization = authorization_header(credentials)
    prefixo = "Bearer "
    if not authorization or not authorization.startswith(prefixo):
        raise HTTPException(
            status_code=401,
            detail={"ok": False, "error": "nao_autorizado"},
        )

    token_recebido = authorization[len(prefixo):].strip()
    if token_recebido != token_esperado:
        raise HTTPException(
            status_code=401,
            detail={"ok": False, "error": "nao_autorizado"},
        )

    return {
        "ok": True,
        "hogar": read_status_sefaz_json("/opt/agente-divina/config/hogar_status.json"),
        "ttf": read_status_sefaz_json("/opt/agente-divina/config/ttf_status.json"),
    }

