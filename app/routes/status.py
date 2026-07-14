from __future__ import annotations

from fastapi import APIRouter


router = APIRouter()


@router.get("/status")
def status():
    return {"status": "online", "agente": "divina"}


@router.get("/health")
def health():
    return {"health": "ok"}

