import os

from fastapi.security import HTTPAuthorizationCredentials

from app.runtime.registry import register
from app.routes.compact import CompactOperationRequest, compact_admin


SERVICE_ALIASES = {
    "agentos": "agentos-worker.service",
    "agentos-worker": "agentos-worker.service",
    "agente-divina": "agente-divina-api.service",
    "agente-divina-api": "agente-divina-api.service",
    "agente-divina-v2": "agente-divina-v2.service",
    "agente-mestre": "agente-mestre.service",
    "agente-mestre-worker": "agente-mestre-worker.service",
}


def _credentials():
    token = os.getenv("AGENTE_ADMIN_TOKEN")

    if not token:
        raise RuntimeError("AGENTE_ADMIN_TOKEN não configurado no serviço.")

    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def _service_name(service):
    value = str(service or "").strip()

    if not value:
        raise ValueError("Serviço não informado.")

    normalized = value.removesuffix(".service")
    return SERVICE_ALIASES.get(normalized, value)


def _admin(operation, **kwargs):
    payload = CompactOperationRequest(
        operation=operation,
        **kwargs,
    )

    return compact_admin(
        payload=payload,
        credentials=_credentials(),
    )


def admin_capabilities():
    return _admin("capabilities")


def service_status(service="agente-divina-api.service"):
    return _admin(
        "service_status",
        service=_service_name(service),
    )


def service_logs(service="agente-divina-api.service", limit=120):
    return _admin(
        "service_logs",
        service=_service_name(service),
        limit=max(1, min(int(limit), 500)),
    )


def service_restart(service="agente-divina-api.service"):
    return _admin(
        "service_restart",
        service=_service_name(service),
    )


def deploy_validate():
    return _admin("validate_v2")


def nginx_test():
    return _admin("nginx_test")


def nginx_reload():
    return _admin("nginx_reload")


register("admin.capabilities", admin_capabilities)
register("service.status", service_status)
register("service.logs", service_logs)
register("service.restart", service_restart)
register("deploy.validate", deploy_validate)
register("nginx.test", nginx_test)
register("nginx.reload", nginx_reload)
