from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


PlanBuilder = Callable[[str], list[dict]]


@dataclass(frozen=True)
class RegisteredIntent:
    name: str
    builder: PlanBuilder
    description: str = ""


class CapabilityPlanRegistry:

    def __init__(self):
        self._intents: dict[str, RegisteredIntent] = {}

    def register(
        self,
        name: str,
        builder: PlanBuilder,
        description: str = "",
    ) -> None:

        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("Nome da intenção não pode ser vazio.")

        self._intents[normalized] = RegisteredIntent(
            name=normalized,
            builder=builder,
            description=description,
        )

    def build(
        self,
        intent_name: str,
        goal: str,
    ) -> list[dict]:

        normalized = intent_name.strip().lower()
        registered = self._intents.get(normalized)

        if registered is None:
            raise KeyError(
                f"Intenção não registrada: {intent_name}"
            )

        return registered.builder(goal)

    def has(self, intent_name: str) -> bool:
        return intent_name.strip().lower() in self._intents

    def list(self) -> list[dict]:
        return [
            {
                "name": item.name,
                "description": item.description,
            }
            for item in self._intents.values()
        ]
