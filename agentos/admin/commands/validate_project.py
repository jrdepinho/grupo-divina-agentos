import importlib

from agentos.admin.registry import register
from agentos.admin.shell import run_command


@register("validate_project")
def validate_project(payload):
    modules = [
        "agentos.core.database",
        "agentos.repositories.mission_repository",
        "agentos.services.mission_service",
        "agentos.services.admin_service",
        "agentos.executors.registry",
        "agentos.executors.dispatcher",
        "agentos.executors.admin",
        "agentos.worker.runner",
    ]

    imports = []

    for module_name in modules:
        try:
            importlib.import_module(module_name)
            imports.append({
                "module": module_name,
                "success": True,
            })
        except Exception as exc:
            imports.append({
                "module": module_name,
                "success": False,
                "error": str(exc),
            })

    database_check = run_command(
        [
            "sqlite3",
            "agentos/data/agentos.db",
            "PRAGMA integrity_check;",
        ],
        timeout=30,
    )

    imports_ok = all(item["success"] for item in imports)
    database_ok = (
        database_check["success"]
        and database_check["stdout"].strip().lower() == "ok"
    )

    return {
        "success": imports_ok and database_ok,
        "imports": imports,
        "database": database_check,
    }
