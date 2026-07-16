from __future__ import annotations

from app.runtime.agentos.router.intent_router import IntentRouter
from app.runtime.agentos.planner.capability_registry import (
    CapabilityPlanRegistry,
)
from app.runtime.agentos.planner.plans import (
    chat_plan,
    search_plan,
    read_plan,
    compile_plan,
    capabilities_plan,
    developer_plan,
)


class Planner:

    def __init__(self):
        self.router = IntentRouter()
        self.registry = CapabilityPlanRegistry()

        self._register_defaults()

    def _register_defaults(self) -> None:

        self.registry.register(
            "chat",
            lambda goal: chat_plan(goal),
            "Executa conversa direta com o modelo LLM.",
        )

        self.registry.register(
            "search",
            lambda goal: search_plan(
                goal.split(" ", 1)[1]
                if " " in goal
                else ""
            ),
            "Pesquisa texto no código-fonte.",
        )

        self.registry.register(
            "read",
            lambda goal: read_plan(
                goal.split(" ", 1)[1]
                if " " in goal
                else ""
            ),
            "Lê um arquivo permitido do projeto.",
        )

        self.registry.register(
            "compile",
            lambda goal: compile_plan(),
            "Compila e valida o projeto.",
        )

        self.registry.register(
            "capabilities",
            lambda goal: capabilities_plan(),
            "Lista as capacidades registradas.",
        )

        self.registry.register(
            "developer",
            lambda goal: developer_plan(goal),
            "Executa o fluxo de desenvolvimento.",
        )

    def build(
        self,
        goal: str,
        context=None,
    ):

        intent = self.router.detect(goal)

        if not self.registry.has(intent.name):
            return self.registry.build(
                "developer",
                goal,
            )

        return self.registry.build(
            intent.name,
            goal,
        )

    def list_registered_intents(self) -> list[dict]:
        return self.registry.list()
