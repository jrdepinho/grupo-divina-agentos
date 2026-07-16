from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Intent:

    name: str
    confidence: float
    requires_llm: bool = False


class IntentRouter:

    CHAT_PREFIXES = (
        "oi",
        "olá",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "quem",
        "o que",
        "qual",
        "quais",
        "como",
        "quando",
        "onde",
        "por que",
        "porque",
        "explique",
        "me explique",
    )

    SEARCH_PREFIXES = (
        "buscar",
        "pesquisar",
        "search",
    )

    READ_PREFIXES = (
        "ler",
        "read",
    )

    COMPILE = (
        "compile",
        "compilar",
        "validar projeto",
        "compile project",
    )

    CAPABILITIES = (
        "capacidades",
        "capabilities",
        "listar capacidades",
        "listar capabilities",
    )

    def detect(self, goal: str) -> Intent:

        text = " ".join(goal.lower().split())

        if text.startswith(self.CHAT_PREFIXES) or text.endswith("?"):
            return Intent(
                "chat",
                0.99,
                True,
            )

        if text.startswith(self.SEARCH_PREFIXES):
            return Intent(
                "search",
                0.95,
            )

        if text.startswith(self.READ_PREFIXES):
            return Intent(
                "read",
                0.95,
            )

        if text in self.COMPILE:
            return Intent(
                "compile",
                0.98,
            )

        if text in self.CAPABILITIES:
            return Intent(
                "capabilities",
                0.98,
            )

        return Intent(
            "developer",
            0.60,
        )
