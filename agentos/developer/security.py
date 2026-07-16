from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path("/opt/agente-divina-v2").resolve()

FORBIDDEN_PARTS = {
    ".git",
    "venv",
    "__pycache__",
    "backup",
    "backups",
    "config",
    "logs",
}

FORBIDDEN_NAMES = {
    ".env",
    "api.env",
    "senhas.env",
    "supabase.env",
}

MAX_WRITE_BYTES = 500_000


def safe_project_path(relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path:
        raise ValueError("Caminho inválido.")

    candidate = (PROJECT_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("Acesso fora do projeto bloqueado.") from exc

    relative_parts = candidate.relative_to(PROJECT_ROOT).parts

    if any(part in FORBIDDEN_PARTS for part in relative_parts):
        raise ValueError("Diretório protegido pela política de segurança.")

    if candidate.name in FORBIDDEN_NAMES or candidate.name.startswith(".env"):
        raise ValueError("Arquivo sensível bloqueado.")

    if candidate.is_symlink():
        raise ValueError("Links simbólicos não são permitidos.")

    return candidate


def validate_content(content: str) -> None:
    if len(content.encode("utf-8")) > MAX_WRITE_BYTES:
        raise ValueError("Conteúdo excede o limite permitido.")
