"""Reusable FastAPI dependencies."""

from __future__ import annotations

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import bearerAuth


def bearer_credentials(
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
) -> HTTPAuthorizationCredentials | None:
    return credentials

