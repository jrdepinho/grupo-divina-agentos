from __future__ import annotations

import re


class DevelopmentStrategy:

    KEYWORDS = {
        "corrigir",
        "implementar",
        "refatorar",
        "criar",
        "gerar",
        "editar",
        "ajustar",
        "alterar",
        "adicionar",
        "compilar",
        "validar",
        "deploy",
        "endpoint",
        "api",
        "bug",
        "erro",
    }

    def matches(self, goal: str) -> bool:
        words = set(
            re.findall(
                r"\b[\wÀ-ÿ]+\b",
                goal.lower(),
                flags=re.UNICODE,
            )
        )
        return bool(words.intersection(self.KEYWORDS))

    def build(self, goal: str, analysis=None):

        plan = [
            {
                "action": "context.read",
                "params": {"goal": goal},
            },
            {
                "action": "developer.search",
                "params": {"text": goal},
            },
            {
                "action": "developer.read",
                "params": {},
            },
        ]

        intent = getattr(analysis, "intent", None)

        if intent == "create":
            plan.append({
                "action": "developer.create",
                "params": {
                    "goal": goal,
                },
            })

        elif intent == "patch":
            plan.extend([
                {
                    "action": "developer.generate_patch",
                    "params": {
                        "goal": goal,
                    },
                },
                {
                    "action": "developer.patch",
                    "params": {},
                },
            ])

        if intent in ("create", "patch", "compile"):
            plan.append({
                "action": "developer.compile",
                "params": {},
            })

        plan.append({
            "action": "developer.validate",
            "params": {},
        })

        return plan
