from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import requests

from app.config import APP_CWD, load_supabase_config


START_TIME = time.time()


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=APP_CWD,
        executable="/bin/bash",
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}


def supabase_rpc(query: str):
    cfg = load_supabase_config()
    url = cfg.get("SUPABASE_URL")
    key = cfg.get("SUPABASE_SERVICE_ROLE_KEY")
    resp = requests.post(
        f"{url}/rest/v1/rpc/execute_select",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={"query": query},
        timeout=60,
    )
    return resp.json()


def read_status_sefaz_json(path: str):
    arquivo = Path(path)
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"erro": "status_nao_encontrado"}
    except Exception as e:
        return {"erro": "status_invalido", "detalhe": str(e)}

