from __future__ import annotations

import os
import socket
import time
from datetime import datetime

from fastapi import APIRouter

from app.utils import START_TIME


router = APIRouter()


@router.get("/runtime")
def runtime():
    return {
        "status": "online",
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "uptime_seconds": int(time.time() - START_TIME),
        "server_time": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/full")
def health_full():
    return {"api": "ok", "runtime": "/runtime", "status": "/status", "health": "/health"}


@router.get("/version")
def version():
    return {"api": "Agente Divina", "version": "1.0.0", "build": "2026-06"}

