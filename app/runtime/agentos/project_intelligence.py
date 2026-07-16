from __future__ import annotations

from typing import Any

from app.project_intelligence.context_builder import (
    build_project_context,
)


PROJECT_ROOT = "/opt/agente-divina-v2"


class ProjectIntelligence:

    def build_context(
        self,
        goal: str,
        path: str | None = None,
        module: str | None = None,
        max_files: int = 5000,
    ) -> dict[str, Any]:

        context = build_project_context(
            path=path or PROJECT_ROOT,
            module=module,
            max_files=max_files,
        )

        context["goal"] = goal

        return context
