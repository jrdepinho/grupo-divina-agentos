from __future__ import annotations

import time
from typing import Any

from app.project_intelligence.context_builder import build_project_context


def generate_architecture_from_context(context_result: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    project_context = context_result.get("project_context", {})
    project = project_context.get("project", {})
    frontend = project_context.get("frontend", {})
    backend = project_context.get("backend", {})
    database = project_context.get("database", {})
    memory = project_context.get("memory", {})
    git = project_context.get("git", {})
    module = context_result.get("module_filter")

    incomplete_modules = []
    for item in project.get("modules", []):
        name = item["name"]
        module_markers = memory.get("by_module", {}).get(name, [])
        if module_markers or item.get("files", 0) <= 2:
            incomplete_modules.append(
                {
                    "name": name,
                    "signals": {
                        "files": item.get("files", 0),
                        "memory_markers": len(module_markers),
                    },
                }
            )

    backlog = [
        "Validar cobertura de testes dos módulos com mais rotas/endpoints.",
        "Consolidar documentação técnica dos fluxos principais.",
        "Priorizar TODO/FIXME por risco operacional.",
        "Mapear contratos de API e payloads críticos.",
    ]
    if database.get("tables") and not database.get("foreign_keys"):
        backlog.append("Revisar relacionamentos explícitos do banco e documentar foreign keys.")
    if backend.get("endpoints") and not backend.get("validations"):
        backlog.append("Criar catálogo de validações por endpoint.")
    if module:
        backlog.insert(0, f"Detalhar dependências e gaps do módulo {module}.")

    markdown = _markdown(project, frontend, backend, database, memory, git, backlog, module)
    warnings = list(context_result.get("warnings", []) or [])
    errors = list(context_result.get("errors", []) or [])

    return {
        "domain": "project_intelligence",
        "capability": "architecture.generate",
        "root": context_result.get("root"),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "context_duration_ms": context_result.get("duration_ms"),
        "module_filter": module,
        "json": {
            "modules_tree": project.get("structure", []),
            "dependencies": project.get("dependencies", {}),
            "functional_flow": {
                "frontend_routes": frontend.get("pages", []),
                "backend_endpoints": backend.get("endpoints", []),
                "database_tables": database.get("tables", []),
            },
            "incomplete_modules": incomplete_modules,
            "suggested_backlog": backlog,
        },
        "markdown": markdown,
        "project_context": project_context,
        "warnings": warnings,
        "errors": errors,
    }


def generate_architecture_with_context(
    path: str | None = None,
    module: str | None = None,
    max_files: int = 5_000,
) -> dict[str, Any]:
    context = build_project_context(path=path, module=module, max_files=max_files)
    return generate_architecture_from_context(context)


def _markdown(
    project: dict[str, Any],
    frontend: dict[str, Any],
    backend: dict[str, Any],
    database: dict[str, Any],
    memory: dict[str, Any],
    git: dict[str, Any],
    backlog: list[str],
    module: str | None,
) -> str:
    title = f"Arquitetura encontrada - {module}" if module else "Arquitetura encontrada"
    lines = [
        f"# {title}",
        "",
        f"- Projeto: `{project.get('root')}`",
        f"- Arquivos analisados: {project.get('files_analyzed', 0)}",
        f"- Módulos encontrados: {project.get('modules_found', 0)}",
        "",
        "## Frontend",
        f"- Frameworks: {', '.join(frontend.get('frameworks') or ['não detectado'])}",
        f"- Páginas: {len(frontend.get('pages', []))}",
        f"- Componentes: {len(frontend.get('components', []))}",
        "",
        "## Backend",
        f"- Frameworks: {', '.join(backend.get('frameworks') or ['não detectado'])}",
        f"- Endpoints: {len(backend.get('endpoints', []))}",
        f"- Services: {len(backend.get('services', []))}",
        "",
        "## Banco",
        f"- ORM: {', '.join(database.get('orm') or ['não detectado'])}",
        f"- Tabelas/modelos: {len(database.get('tables', []))}",
        f"- Migrations: {len(database.get('migrations', []))}",
        "",
        "## Memória e documentação",
        f"- TODO/FIXME/NOTE/ADR: {len(memory.get('markers', []))}",
        f"- Markdown: {len(memory.get('markdown', []))}",
        "",
        "## Git",
        f"- Branch atual: {git.get('current_branch') or 'não detectada'}",
        f"- Hotspots: {len(git.get('hotspots', []))}",
        "",
        "## Roadmap sugerido",
    ]
    lines.extend(f"- {item}" for item in backlog)
    return "\n".join(lines)
