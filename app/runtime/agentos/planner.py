from __future__ import annotations

from typing import List, Dict

from app.runtime.agentos.intent import (
    Intent,
    IntentRouter,
)

router = IntentRouter()

from app.runtime.agentos.plans import (
    build_status_plan,
    build_restart_plan,
    build_deploy_plan,
    build_search_plan,
    build_compile_plan,
    build_create_code_plan,
    build_patch_code_plan,
)




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
    intent = router.detect(goal)

    p = []

    # ---------------------------------------------------
    # STATUS
    # ---------------------------------------------------

    if intent == Intent.STATUS:
        return build_status_plan()

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

    

    if intent == Intent.CREATE_CODE:
        return build_create_code_plan(goal)

    if intent == Intent.PATCH_CODE:
        return build_patch_code_plan(goal)

    if intent == Intent.COMPILE:
        return build_compile_plan()

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

