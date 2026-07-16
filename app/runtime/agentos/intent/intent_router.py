from enum import Enum


class Intent(str, Enum):
    STATUS = "status"
    RESTART = "restart"
    DEPLOY = "deploy"
    SEARCH = "search"
    COMPILE = "compile"
    CREATE_CODE = "create_code"
    PATCH_CODE = "patch_code"
    UNKNOWN = "unknown"


class IntentRouter:

    def detect(self, goal: str) -> Intent:

        g = goal.lower()

        if any(x in g for x in (
            "status",
            "estado",
            "health",
            "diagnóstico",
            "diagnostico",
        )):
            return Intent.STATUS

        if any(x in g for x in (
            "restart",
            "reiniciar",
            "reinicie",
        )):
            return Intent.RESTART

        if any(x in g for x in (
            "deploy",
            "publicar",
            "implantar",
        )):
            return Intent.DEPLOY

        if any(x in g for x in (
            "buscar",
            "pesquisar",
            "search",
        )):
            return Intent.SEARCH

        if any(x in g for x in (
            "compilar",
            "compile",
            "validar",
        )):
            return Intent.COMPILE

        if any(x in g for x in (
            "criar",
            "novo",
            "adicionar",
            "implementar",
        )):
            return Intent.CREATE_CODE

        if any(x in g for x in (
            "corrigir",
            "alterar",
            "editar",
            "refatorar",
            "patch",
        )):
            return Intent.PATCH_CODE

        return Intent.UNKNOWN
