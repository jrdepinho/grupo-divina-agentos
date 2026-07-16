
from __future__ import annotations

from app.runtime.agentos.bootstrap import initialize
from app.runtime.agentos.registry import (
    get,
    list_capabilities as registry_list_capabilities,
)


def dispatch_capability(name: str, payload: dict | None = None):
    initialize()

    capability = get(name)

    if capability is None:
        return {
            "ok": False,
            "error": "capability_not_found",
            "capability": name,
            "available": sorted(registry_list_capabilities()),
        }

    payload = payload or {}

    result = capability.handler(**payload)

    if result is None:
        result = {}

    if not isinstance(result, dict):
        result = {"value": result}

    return {
        "ok": bool(result.get("ok", True)),
        "result": result,
    }


def list_capabilities():
    return [
        {
            "name": name,
        }
        for name in sorted(registry_list_capabilities())
    ]
