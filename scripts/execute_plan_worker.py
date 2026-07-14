#!/usr/bin/env python3
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

JOB_DIR = Path('/opt/agente-divina/logs/jobs')
TOKEN_FILE = Path('/opt/agente-divina/config/supabase.env')


def now() -> str:
    return datetime.datetime.now().isoformat()


def append(path: Path, text: str) -> None:
    with path.open('a', encoding='utf-8') as f:
        f.write(text + '\n')


def read_token() -> str:
    for line in TOKEN_FILE.read_text().splitlines():
        if line.startswith('AGENTE_ADMIN_TOKEN='):
            return line.split('=', 1)[1]
    raise RuntimeError('AGENTE_ADMIN_TOKEN não encontrado')


def main() -> int:
    if len(sys.argv) < 3:
        print('usage: execute_plan_worker.py JOB_ID PAYLOAD_JSON', file=sys.stderr)
        return 2

    job_id = sys.argv[1]
    payload = json.loads(sys.argv[2])
    root = JOB_DIR / job_id
    root.mkdir(parents=True, exist_ok=True)
    status_path = root / 'status.json'
    stdout_path = root / 'stdout.log'
    stderr_path = root / 'stderr.log'
    exit_path = root / 'exitcode.txt'

    status = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'job_id': job_id}
    status.update({'state': 'running', 'started_at': now(), 'worker': 'execute_plan_worker'})
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

    append(stdout_path, f'--- execute_plan_worker started {now()} ---')
    append(stdout_path, 'payload=' + json.dumps(payload, ensure_ascii=False))

    token = read_token()
    cmd = [
        'curl', '-s', '--max-time', '900', '-X', 'POST',
        'http://127.0.0.1:8000/admin/full-access',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload, ensure_ascii=False),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=960)
    stdout_path.write_text(stdout_path.read_text(errors='replace') + proc.stdout, encoding='utf-8')
    if proc.stderr:
        stderr_path.write_text(stderr_path.read_text(errors='replace') + proc.stderr, encoding='utf-8')

    ok = False
    result = None
    try:
        result = json.loads(proc.stdout)
        ok = bool(result.get('ok')) and proc.returncode == 0
    except Exception as exc:
        append(stderr_path, f'falha ao interpretar resposta JSON: {exc}')

    code = 0 if ok else (proc.returncode or 1)
    exit_path.write_text(str(code), encoding='utf-8')
    status.update({
        'state': 'completed' if code == 0 else 'failed',
        'exitcode': code,
        'finished_at': now(),
        'http_returncode': proc.returncode,
        'result_ok': ok,
        'result_summary': result if isinstance(result, dict) else None,
    })
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    append(stdout_path, f'--- execute_plan_worker finished code={code} {now()} ---')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
