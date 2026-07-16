from __future__ import annotations

from typing import Any


class ContextReducer:

    def reduce(
        self,
        goal: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:

        project_context = context.get("project_context")

        if project_context:

            project = project_context.get("project", {})

            return {
                "goal": goal,
                "summary": project_context.get("summary", {}),
                "modules": [
                    {
                        "name": path,
                        "files": 1,
                    }
                    for path in project.get("files", [])
                ],
                "services": project.get("services", []),
                "todos": project.get("todo", []),
            }

        #
        # Compatibilidade com o formato antigo
        #
        return {
            "goal": goal,
            "summary": context.get("summary", {}),
            "modules": context.get("selected_modules", []),
            "services": context.get("services", []),
            "todos": context.get("todo", []),
        }
