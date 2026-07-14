from __future__ import annotations

from typing import List, Dict


def step(action, **kwargs):
    return {
        "action": action,
        "args": kwargs,
    }


def contains(goal, *words):
    g = goal.lower()
    return any(w in g for w in words)


def plan(goal: str) -> List[Dict]:

    g = goal.lower().strip()

    p = []

    # ---------------------------------------------------
    # STATUS
    # ---------------------------------------------------

    if contains(g,
        "status",
        "estado",
        "health",
        "diagnostico",
        "diagnóstico",
    ):

        p.append(step(
            "service.status",
            service="agente-divina-api.service"
        ))

        p.append(step(
            "service.logs",
            service="agente-divina-api.service",
            limit=100
        ))

        return p

    # ---------------------------------------------------
    # RESTART
    # ---------------------------------------------------

    if contains(g,
        "restart",
        "reinicie",
        "reiniciar",
        "reinicia",
    ):

        p.append(step(
            "service.restart",
            service="agente-divina-api.service"
        ))

        # O próprio serviço será reiniciado; o dispatcher encerra
        # a execução imediatamente após disparar o restart.
        return p

    # ---------------------------------------------------
    # DEPLOY
    # ---------------------------------------------------

    if contains(g,
        "deploy",
        "publicar",
        "implantar",
        "atualizar",
    ):

        p.append(step("deploy.validate"))

        p.append(step("developer.compile"))

        p.append(step(
            "service.restart",
            service="agente-divina-api.service"
        ))

        p.append(step(
            "service.status",
            service="agente-divina-api.service"
        ))

        return p

    # ---------------------------------------------------
    # COMPILAR
    # ---------------------------------------------------

    if contains(g,
        "compilar",
        "compile",
        "validar",
    ):

        p.append(step("developer.compile"))

        p.append(step("developer.validate"))

        return p

    # ---------------------------------------------------
    # PESQUISAR
    # ---------------------------------------------------

    if g.startswith("buscar "):

        texto = goal[7:]

        p.append(step(
            "developer.search",
            text=texto,
        ))

        return p

    # ---------------------------------------------------
    # PADRÃO
    # ---------------------------------------------------

    p.append(step(
        "goal.echo",
        goal=goal,
    ))

    return p

