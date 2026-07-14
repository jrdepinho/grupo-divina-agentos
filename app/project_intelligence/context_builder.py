from __future__ import annotations

import time
from typing import Any

from app.project_intelligence.scanners import (
    inspect_git,
    scan_backend,
    scan_database,
    scan_frontend,
    scan_memory,
    scan_project,
)


def build_project_context(
    path: str | None = None,
    module: str | None = None,
    max_files: int = 5_000,
) -> dict[str, Any]:
    started = time.perf_counter()
    project = scan_project(path, max_files=max_files)
    frontend = scan_frontend(path, max_files=max_files)
    backend = scan_backend(path, max_files=max_files)
    database = scan_database(path, max_files=max_files)
    memory = scan_memory(path, max_files=max_files)
    git = inspect_git(path)

    modules = project.get("modules", [])
    module_filter = (module or "").strip().lower()
    selected_modules = [
        item
        for item in modules
        if not module_filter or module_filter in str(item.get("name", "")).lower()
    ]

    warnings = []
    errors = []
    for scan in (project, frontend, backend, database, memory, git):
        warnings.extend(scan.get("warnings", []) or [])
        errors.extend(scan.get("errors", []) or [])

    return {
        "domain": "project_intelligence",
        "capability": "context.build",
        "root": project.get("root"),
        "module_filter": module,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "files_analyzed": project.get("files_analyzed", 0),
        "modules_found": project.get("modules_found", 0),
        "project_context": {
            "project": project,
            "frontend": frontend,
            "backend": backend,
            "database": database,
            "memory": memory,
            "git": git,
            "selected_modules": selected_modules,
            "summary": {
                "frontend_frameworks": frontend.get("frameworks", []),
                "backend_frameworks": backend.get("frameworks", []),
                "database_orm": database.get("orm", []),
                "routes": len(project.get("routes", [])),
                "endpoints": len(backend.get("endpoints", [])),
                "tables": len(database.get("tables", [])),
                "memory_markers": len(memory.get("markers", [])),
                "git_hotspots": len(git.get("hotspots", [])),
            },
        },
        "warnings": warnings,
        "errors": errors,
    }
