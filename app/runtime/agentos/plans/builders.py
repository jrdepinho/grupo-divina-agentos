from typing import Dict, List


def step(action: str, **kwargs):
    return {
        "action": action,
        "args": kwargs,
    }


def build_status_plan() -> List[Dict]:
    return [
        step(
            "service.status",
            service="agente-divina-api.service",
        ),
        step(
            "service.logs",
            service="agente-divina-api.service",
            limit=100,
        ),
    ]


def build_restart_plan() -> List[Dict]:
    return [
        step(
            "service.restart",
            service="agente-divina-api.service",
        )
    ]


def build_deploy_plan() -> List[Dict]:
    return [
        step("deploy.run")
    ]


def build_search_plan() -> List[Dict]:
    return [
        step("developer.search")
    ]


def build_compile_plan() -> List[Dict]:
    return [
        step("developer.compile")
    ]


def build_create_code_plan(goal: str) -> List[Dict]:
    return [
        step(
            "developer.search",
            text=goal,
        ),
        step(
            "developer.write",
            text=goal,
        ),
        step(
            "developer.compile",
            text=goal,
        ),
        step(
            "developer.validate",
            text=goal,
        ),
    ]


def build_patch_code_plan(goal: str) -> List[Dict]:
    return [
        step(
            "developer.search",
            text=goal,
        ),
        step(
            "developer.patch",
            text=goal,
        ),
        step(
            "developer.compile",
            text=goal,
        ),
        step(
            "developer.validate",
            text=goal,
        ),
    ]
