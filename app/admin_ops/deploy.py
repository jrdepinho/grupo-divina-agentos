from __future__ import annotations
from typing import Any, Callable

def handle_deploy_op(req: Any, run_cmd: Callable[..., dict]):
    op=req.operation
    cwd=req.path or '/opt/agente-divina-v2'
    if op in {'project_build','deploy_build'}:
        return {'ok':True,'result':run_cmd('npm run build',cwd=cwd)}
    if op in {'project_test','deploy_test'}:
        cmd=req.command or 'npm test -- --watch=false'
        return {'ok':True,'result':run_cmd(cmd,cwd=cwd)}
    if op in {'project_healthcheck','deploy_healthcheck'}:
        url=(req.args or {}).get('url') or 'https://grupo-divina-dashboard.vercel.app/auth/login'
        return {'ok':True,'result':run_cmd(f'curl -s -I {url} | head -30')}
    return None