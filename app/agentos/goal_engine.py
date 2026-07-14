from __future__ import annotations

import json
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/opt/agente-divina-v2")

AUDIT = PROJECT_ROOT / "logs" / "goal_engine.jsonl"

AUDIT.parent.mkdir(parents=True, exist_ok=True)


def audit(event, payload):
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "time": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload
        }, ensure_ascii=False) + "\n")


def run(cmd):
    p = subprocess.run(
        cmd,
        shell=False,
        capture_output=True,
        text=True
    )

    return {
        "ok": p.returncode == 0,
        "stdout": p.stdout,
        "stderr": p.stderr,
        "exit_code": p.returncode
    }


def capabilities():

    return {

        "version": "goal-engine-v1",

        "files": {
            "read": True,
            "write": True,
            "patch": True
        },

        "services": {
            "status": True,
            "restart": True,
            "logs": True
        },

        "validation": {
            "python_compile": True,
            "nginx_test": True
        },

        "openapi": {
            "slim": True
        }

    }


def health():

    return {
        "status": "healthy",
        "engine": "goal"
    }


def version():

    return {
        "version": "goal-engine-v1"
    }


def status():

    return {
        "status": "ok"
    }
