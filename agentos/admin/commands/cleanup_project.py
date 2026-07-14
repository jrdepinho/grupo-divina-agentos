import shutil
from pathlib import Path

from agentos.admin.context import PROJECT_ROOT
from agentos.admin.registry import register


@register("cleanup_project")
def cleanup_project(payload):

    removidos = []

    for pattern in (
        "**/__pycache__",
        "**/*.pyc",
    ):
        for item in PROJECT_ROOT.glob(pattern):

            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

                removidos.append(str(item.relative_to(PROJECT_ROOT)))

            except Exception:
                pass

    return {
        "success": True,
        "removed": removidos,
        "count": len(removidos),
    }
