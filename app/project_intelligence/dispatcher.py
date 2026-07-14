from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.project_intelligence.architecture import generate_architecture_with_context
from app.project_intelligence.context_builder import build_project_context
from app.project_intelligence.scanners import (
    inspect_git,
    scan_backend,
    scan_database,
    scan_frontend,
    scan_memory,
    scan_project,
)


Handler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class Capability:
    name: str
    domain: str
    description: str
    handler: Handler


def _path(payload: dict[str, Any]) -> str | None:
    value = payload.get("path") or payload.get("root")
    return str(value) if value else None


def _max_files(payload: dict[str, Any]) -> int:
    try:
        return max(1, min(int(payload.get("max_files") or 5_000), 25_000))
    except Exception:
        return 5_000


def _project(payload: dict[str, Any]) -> dict[str, Any]:
    return scan_project(_path(payload), max_files=_max_files(payload))


def _frontend(payload: dict[str, Any]) -> dict[str, Any]:
    return scan_frontend(_path(payload), max_files=_max_files(payload))


def _backend(payload: dict[str, Any]) -> dict[str, Any]:
    return scan_backend(_path(payload), max_files=_max_files(payload))


def _database(payload: dict[str, Any]) -> dict[str, Any]:
    return scan_database(_path(payload), max_files=_max_files(payload))


def _memory(payload: dict[str, Any]) -> dict[str, Any]:
    return scan_memory(_path(payload), max_files=_max_files(payload))


def _git(payload: dict[str, Any]) -> dict[str, Any]:
    return inspect_git(_path(payload))


def _context(payload: dict[str, Any]) -> dict[str, Any]:
    module = payload.get("module")
    return build_project_context(_path(payload), module=str(module) if module else None, max_files=_max_files(payload))


def _architecture(payload: dict[str, Any]) -> dict[str, Any]:
    module = payload.get("module")
    return generate_architecture_with_context(_path(payload), module=str(module) if module else None, max_files=_max_files(payload))


CAPABILITIES: dict[str, Capability] = {
    "project.scan": Capability("project.scan", "project_intelligence", "Inventaria estrutura, módulos, docs, dependências, APIs e rotas.", _project),
    "frontend.scan": Capability("frontend.scan", "project_intelligence", "Detecta frameworks frontend e mapeia páginas, componentes e stores.", _frontend),
    "backend.scan": Capability("backend.scan", "project_intelligence", "Detecta frameworks backend e mapeia endpoints, services e regras.", _backend),
    "database.scan": Capability("database.scan", "project_intelligence", "Mapeia ORM, migrations, tabelas, índices e relacionamentos sem alterar banco.", _database),
    "memory.search": Capability("memory.search", "project_intelligence", "Pesquisa TODO, FIXME, NOTE, ADR e documentação por módulo.", _memory),
    "git.inspect": Capability("git.inspect", "project_intelligence", "Inspeciona branches, histórico, autores e hotspots.", _git),
    "context.build": Capability("context.build", "project_intelligence", "Consolida scans em um project_context único para o motor de arquitetura.", _context),
    "architecture.generate": Capability("architecture.generate", "project_intelligence", "Gera arquitetura, gaps, backlog e roadmap em JSON e Markdown.", _architecture),
}


def list_capabilities() -> list[dict[str, str]]:
    return [
        {
            "name": item.name,
            "domain": item.domain,
            "description": item.description,
        }
        for item in CAPABILITIES.values()
    ]


def dispatch_capability(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    capability = CAPABILITIES.get(name)
    if capability is None:
        return {
            "ok": False,
            "error": "capability_not_found",
            "capability": name,
            "available": sorted(CAPABILITIES),
        }

    result = capability.handler(payload or {})
    result.setdefault("domain", capability.domain)
    result.setdefault("capability", capability.name)
    result["dispatch_duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return {"ok": not result.get("errors"), "result": result}
