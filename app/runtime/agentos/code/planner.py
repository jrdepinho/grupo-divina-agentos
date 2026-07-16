from __future__ import annotations

from typing import Any


class CodePlanner:
    """
    Responsável por transformar intenções de desenvolvimento
    em operações concretas para o DeveloperEngine.
    """

    def plan(self, action: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "CodePlanner ainda não implementado."
        )
