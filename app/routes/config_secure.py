from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from fastapi import APIRouter, Security
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import bearerAuth, verify_admin_token


router = APIRouter()

CONFIG_PATHS = (
    Path("/opt/agente-divina-v2/config/api.env"),
    Path("/opt/agente-divina-v2/config/supabase.env"),
    Path("/opt/agente-divina/config/api.env"),
    Path("/opt/agente-divina/config/supabase.env"),
)
CONFIG_KEYS = (
    "AGENTE_ADMIN_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_DB_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_ANON_KEY",
    "DATABASE_URL",
)


def _mask(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 10:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def _file_values(path: Path) -> dict[str, str | None]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        return dict(dotenv_values(path))
    except Exception:
        return {}


def _source_for_key(key: str) -> dict[str, Any]:
    env_value = os.getenv(key)
    if env_value:
        return {
            "configured": True,
            "source": "environment",
            "masked": _mask(env_value),
            "length": len(env_value),
        }

    found_files: list[dict[str, Any]] = []
    for path in CONFIG_PATHS:
        values = _file_values(path)
        value = values.get(key)
        if value:
            found_files.append({
                "path": str(path),
                "masked": _mask(value),
                "length": len(value),
            })

    if found_files:
        return {
            "configured": True,
            "source": "file",
            "files": found_files,
        }

    return {
        "configured": False,
        "source": None,
    }


@router.get(
    "/admin/config/summary",
    summary="Resumo seguro da configuração do ambiente",
    description=(
        "Retorna apenas metadados seguros sobre variáveis e arquivos de configuração, "
        "sem expor segredos completos. Útil para diagnosticar divergências entre "
        "DigitalOcean, Supabase, Vercel e Actions do GPT."
    ),
)
def admin_config_summary(
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    verify_admin_token(credentials)

    files = []
    for path in CONFIG_PATHS:
        exists = path.exists()
        files.append({
            "path": str(path),
            "exists": exists,
            "is_file": path.is_file() if exists else False,
            "readable": bool(_file_values(path)) if exists and path.is_file() else False,
        })

    return {
        "ok": True,
        "keys": {key: _source_for_key(key) for key in CONFIG_KEYS},
        "config_files": files,
        "notes": [
            "Valores sensíveis são mascarados e nunca retornados integralmente.",
            "Se uma chave aparecer em environment e arquivo, environment tem precedência no código Python.",
        ],
    }
