#!/usr/bin/env python3
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

JOB_DIR = Path('/opt/agente-divina/logs/jobs')

def now() -> str:
    return datetime.datetime.now().isoformat()

def run(cmd: list[str] | str, stdout_path: Path, stderr_path: Path) -> int:
    with stdout_path.open('ab') as out, stderr_path.open('ab') as err:
        if isinstance(cmd, str):
            p = subprocess.run(cmd, shell=True, stdout=out, stderr=err)
        else:
            p = subprocess.run(cmd, stdout=out, stderr=err)
        return int(p.returncode)

def append(path: Path, text: str) -> None:
    with path.open('a', encoding='utf-8') as f:
        f.write(text + '\n')

def main() -> int:
    if len(sys.argv) < 5:
        print('usage: service_restart_worker.py JOB_ID SERVICE HEALTH_URL WAIT_SECONDS', file=sys.stderr)
        return 2
    job_id, service, health_url, wait_s = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    root = JOB_DIR / job_id
    root.mkdir(parents=True, exist_ok=True)
    status_path = root / 'status.json'
    stdout_path = root / 'stdout.log'
    stderr_path = root / 'stderr.log'
    exit_path = root / 'exitcode.txt'

    status = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'job_id': job_id}
    status.update({'state': 'running', 'started_at': now(), 'worker_pid': None})
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

    append(stdout_path, f'--- worker started {now()} ---')
    append(stdout_path, f'service={service}')
    append(stdout_path, f'health_url={health_url}')

    append(stdout_path, '--- restart service ---')
    rc = run(['/bin/systemctl', 'restart', service], stdout_path, stderr_path)
    append(stdout_path, f'restart_returncode={rc}')

    append(stdout_path, '--- wait active ---')
    active = False
    for i in range(1, wait_s + 1):
        proc = subprocess.run(['/bin/systemctl', 'is-active', service], capture_output=True, text=True)
        state = (proc.stdout or '').strip()
        append(stdout_path, f'attempt={i} state={state}')
        if state == 'active':
            active = True
            break
        time.sleep(1)
    if not active:
        append(stderr_path, f'service not active after {wait_s}s')
        exit_path.write_text('1', encoding='utf-8')
        status.update({'state': 'failed', 'exitcode': 1, 'finished_at': now()})
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        return 1

    append(stdout_path, '--- healthcheck ---')
    healthy = False
    for i in range(1, wait_s + 1):
        proc = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', health_url], capture_output=True, text=True)
        code = (proc.stdout or '').strip()
        append(stdout_path, f'attempt={i} http={code}')
        if code == '200':
            healthy = True
            break
        time.sleep(1)

    code = 0 if healthy else 1
    if not healthy:
        append(stderr_path, f'healthcheck failed: {health_url}')
    exit_path.write_text(str(code), encoding='utf-8')
    status.update({'state': 'completed' if code == 0 else 'failed', 'exitcode': code, 'finished_at': now()})
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    append(stdout_path, f'--- worker finished code={code} {now()} ---')
    return code

if __name__ == '__main__':
    raise SystemExit(main())
