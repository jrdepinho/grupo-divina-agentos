from __future__ import annotations

from dataclasses import dataclass

from app.runtime.agentos.keyword_expander import KeywordExpander

STOP_WORDS = {
    "corrigir",
    "criar",
    "fazer",
    "adicionar",
    "melhorar",
    "atualizar",
    "remover",
    "de",
    "do",
    "da",
    "no",
    "na",
    "o",
    "a",
    "os",
    "as",
    "um",
    "uma",
    "bug",
    "erro",
}


@dataclass
class GoalAnalysis:
    intent: str
    keywords: list[str]


class GoalAnalyzer:

    def analyze(self, goal: str) -> GoalAnalysis:

        goal_lower = goal.lower().strip()
        normalized_goal = " ".join(goal_lower.split())

        create_prefixes = (
            "criar",
            "crie",
            "gera",
            "gerar",
            "novo",
            "nova",
            "construir",
            "construa",
        )

        patch_prefixes = (
            "corrigir",
            "corrija",
            "corrige",
            "ajustar",
            "ajuste",
            "editar",
            "edite",
            "alterar",
            "altere",
            "refatorar",
            "implementar",
            "implemente",
            "adicionar",
            "adicione",
            "atualizar",
            "atualize",
            "substituir",
            "remover",
            "remova",
        )

        compile_prefixes = (
            "compilar",
            "compile",
            "build",
            "validar",
        )

        deploy_prefixes = (
            "deploy",
            "publicar",
            "release",
        )

        chat_prefixes = (
            "explique",
            "explique-me",
            "o que",
            "quem",
            "qual",
            "como",
            "por que",
            "porque",
            "diga",
            "responda",
            "escreva",
        )

        if normalized_goal.startswith(create_prefixes):
            intent = "create"

        elif normalized_goal.startswith(patch_prefixes):
            intent = "patch"

        elif normalized_goal.startswith(compile_prefixes):
            intent = "compile"

        elif normalized_goal.startswith(deploy_prefixes):
            intent = "deploy"

        elif normalized_goal.startswith(chat_prefixes):
            intent = "chat"

        else:
            intent = "unknown"

        keywords = [
            word
            for word in goal_lower.split()
            if word not in STOP_WORDS
        ]

        keywords = KeywordExpander().expand(keywords)

        return GoalAnalysis(
            intent=intent,
            keywords=keywords,
        )
