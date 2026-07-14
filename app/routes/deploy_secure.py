from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.auth import bearerAuth, verify_admin_token


router = APIRouter()

AUDIT_LOG = Path("/opt/agente-divina/logs/admin_actions.log")
DEPLOY_BACKUP_DIR = Path("/opt/agente-divina/backups")
DEPLOY_PACKAGE_DIR = Path("/opt/agente-divina-v2/packages")
ALLOWED_DEPLOY_ROOTS = (Path("/opt/agente-divina-v2"),)
ALLOWED_PACKAGE_ROOTS = (DEPLOY_BACKUP_DIR, DEPLOY_PACKAGE_DIR)


class AdminDeployPackageRequest(BaseModel):
    target: str = "/opt/agente-divina-v2"
    label: str = "manual"


class AdminDeployApplyRequest(BaseModel):
    package_path: str
    target: str = "/opt/agente-divina-v2"
    compile_python: bool = True


class AdminDeployRollbackRequest(BaseModel):
    backup_path: str
    target: str = "/opt/agente-divina-v2"
    compile_python: bool = True


def _require_admin(credentials: HTTPAuthorizationCredentials | None) -> None:
    verify_admin_token(credentials)


def _audit(action: str, detail: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "detail": detail,
    }
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve(raw_path: str) -> Path:
    if not raw_path or not str(raw_path).strip():
        raise HTTPException(status_code=400, detail="path obrigatório")
    return Path(str(raw_path)).expanduser().resolve()


def _validate_inside(raw_path: str, roots: tuple[Path, ...], kind: str) -> Path:
    path = _resolve(raw_path)
    resolved_roots = tuple(root.resolve() for root in roots)
    if not any(_is_relative_to(path, root) or path == root for root in resolved_roots):
        raise HTTPException(
            status_code=403,
            detail={
                "erro": f"{kind} fora dos diretórios permitidos",
                "path": str(path),
                "allowed_roots": [str(root) for root in resolved_roots],
            },
        )
    return path


def _validate_target(raw_target: str) -> Path:
    target = _validate_inside(raw_target, ALLOWED_DEPLOY_ROOTS, "target")
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail={"erro": "target não encontrado", "target": str(target)})
    return target


def _validate_package(raw_package: str) -> Path:
    package = _validate_inside(raw_package, ALLOWED_PACKAGE_ROOTS, "package")
    if not package.exists() or not package.is_file():
        raise HTTPException(status_code=404, detail={"erro": "package não encontrado", "package": str(package)})
    if not str(package).endswith((".tar.gz", ".tgz")):
        raise HTTPException(status_code=400, detail="package deve ser .tar.gz ou .tgz")
    return package


def _safe_label(label: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in str(label or "manual"))
    return cleaned.strip("-")[:60] or "manual"


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def _should_skip(path: Path, target: Path) -> bool:
    rel = path.relative_to(target)
    parts = set(rel.parts)
    if "venv" in parts or "__pycache__" in parts or ".git" in parts or "packages" in parts:
        return True
    if path.suffix in {".pyc", ".pyo"}:
        return True
    return False


def _create_tar_from_target(target: Path, output: Path) -> dict[str, Any]:
    count = 0
    bytes_total = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as tar:
        for item in target.rglob("*"):
            if _should_skip(item, target):
                continue
            arcname = target.name / item.relative_to(target)
            tar.add(item, arcname=str(arcname), recursive=False)
            count += 1
            if item.is_file():
                bytes_total += item.stat().st_size
    return {"files": count, "source_bytes": bytes_total, "package_bytes": output.stat().st_size}


def _validate_tar_safety(package: Path) -> None:
    try:
        with tarfile.open(package, "r:gz") as tar:
            for member in tar.getmembers():
                name = member.name
                member_path = Path(name)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise HTTPException(status_code=400, detail={"erro": "package contém caminho inseguro", "member": name})
                if member.issym() or member.islnk():
                    raise HTTPException(status_code=400, detail={"erro": "package contém link não permitido", "member": name})
    except tarfile.TarError as exc:
        raise HTTPException(status_code=400, detail=f"package tar inválido: {exc}") from exc


def _copy_tree_contents(source: Path, target: Path) -> int:
    copied = 0
    for item in source.rglob("*"):
        rel = item.relative_to(source)
        if not rel.parts:
            continue
        destination = target / rel
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)
            copied += 1
    return copied


def _detect_source_dir(extract_dir: Path, target: Path) -> Path:
    candidate = extract_dir / target.name
    if candidate.exists() and candidate.is_dir():
        return candidate
    children = [child for child in extract_dir.iterdir() if child.is_dir()]
    if len(children) == 1:
        return children[0]
    return extract_dir


def _compile_main(target: Path) -> dict[str, Any]:
    import subprocess

    proc = subprocess.run(
        ["python3", "-m", "py_compile", str(target / "app" / "main.py")],
        shell=False,
        cwd=str(target),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def _make_backup(target: Path, label: str) -> Path:
    backup = DEPLOY_BACKUP_DIR / f"{target.name}-{_safe_label(label)}-{_timestamp()}.tar.gz"
    _create_tar_from_target(target, backup)
    return backup


@router.post("/admin/deploy/package")
def admin_deploy_package(
    payload: AdminDeployPackageRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    _require_admin(credentials)
    target = _validate_target(payload.target)
    label = _safe_label(payload.label)
    package = DEPLOY_BACKUP_DIR / f"{target.name}-{label}-{_timestamp()}.tar.gz"
    stats = _create_tar_from_target(target, package)
    result = {"ok": True, "target": str(target), "package": str(package), **stats}
    _audit("deploy.package", result)
    return result


@router.post("/admin/deploy/apply")
def admin_deploy_apply(
    payload: AdminDeployApplyRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    _require_admin(credentials)
    target = _validate_target(payload.target)
    package = _validate_package(payload.package_path)
    _validate_tar_safety(package)

    backup = _make_backup(target, "pre-apply")
    with tempfile.TemporaryDirectory(prefix="agente-deploy-") as tmp:
        extract_dir = Path(tmp)
        with tarfile.open(package, "r:gz") as tar:
            tar.extractall(extract_dir)
        source = _detect_source_dir(extract_dir, target)
        copied = _copy_tree_contents(source, target)

    compile_result = _compile_main(target) if payload.compile_python else None
    if compile_result and not compile_result["ok"]:
        _audit("deploy.apply.failed_compile", {"target": str(target), "package": str(package), "backup": str(backup)})
        return {
            "ok": False,
            "erro": "deploy aplicado, mas compilação falhou; use rollback se necessário",
            "target": str(target),
            "package": str(package),
            "backup": str(backup),
            "copied_files": copied,
            "compile": compile_result,
        }

    result = {
        "ok": True,
        "target": str(target),
        "package": str(package),
        "backup": str(backup),
        "copied_files": copied,
        "compile": compile_result,
    }
    _audit("deploy.apply", result)
    return result


@router.post("/admin/deploy/rollback")
def admin_deploy_rollback(
    payload: AdminDeployRollbackRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(bearerAuth),
):
    _require_admin(credentials)
    target = _validate_target(payload.target)
    backup_package = _validate_package(payload.backup_path)
    _validate_tar_safety(backup_package)

    safety_backup = _make_backup(target, "pre-rollback")
    with tempfile.TemporaryDirectory(prefix="agente-rollback-") as tmp:
        extract_dir = Path(tmp)
        with tarfile.open(backup_package, "r:gz") as tar:
            tar.extractall(extract_dir)
        source = _detect_source_dir(extract_dir, target)
        copied = _copy_tree_contents(source, target)

    compile_result = _compile_main(target) if payload.compile_python else None
    result = {
        "ok": bool(compile_result["ok"] if compile_result else True),
        "target": str(target),
        "rollback_from": str(backup_package),
        "safety_backup": str(safety_backup),
        "copied_files": copied,
        "compile": compile_result,
    }
    _audit("deploy.rollback", result)
    return result
