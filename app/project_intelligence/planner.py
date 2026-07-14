from __future__ import annotations

import re
from typing import Any


PROJECT_INTELLIGENCE_SCAN_SEQUENCE = [
    "project.scan",
    "frontend.scan",
    "backend.scan",
    "database.scan",
    "memory.search",
    "git.inspect",
]

PROJECT_INTELLIGENCE_SEQUENCE = [
    "context.build",
    "architecture.generate",
]

GOAL_TRIGGERS = (
    "analise o modulo",
    "analise o módulo",
    "analisar modulo",
    "analisar módulo",
    "continuar implantacao",
    "continuar implantação",
    "reconstruir modulo",
    "reconstruir módulo",
    "entender arquitetura",
    "levantar dependencias",
    "levantar dependências",
)


def _normalize(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def should_use_project_intelligence(goal: str) -> bool:
    normalized = _normalize(goal)
    return any(trigger in normalized for trigger in GOAL_TRIGGERS)


def extract_module(goal: str) -> str | None:
    match = re.search(r"m[oó]dulo\s+([A-Za-z0-9_.\-/ ]+)", goal or "", flags=re.I)
    if not match:
        return None
    module = re.split(r"\s+(?:e|com|para|antes|depois)\s+", match.group(1).strip(), maxsplit=1)[0]
    return module.strip(" .") or None


def build_project_intelligence_plan(goal: str, path: str | None = None) -> dict[str, Any]:
    triggered = should_use_project_intelligence(goal)
    module = extract_module(goal)
    steps = [
        {
            "order": index + 1,
            "capability": capability,
            "status": "pending",
            "input": {"path": path, "module": module},
        }
        for index, capability in enumerate(PROJECT_INTELLIGENCE_SEQUENCE)
    ]
    return {
        "domain": "project_intelligence",
        "triggered": triggered,
        "goal": goal,
        "module": module,
        "plan": steps if triggered else [],
        "scan_sequence": PROJECT_INTELLIGENCE_SCAN_SEQUENCE if triggered else [],
        "reason": "GOAL solicita entendimento de projeto/arquitetura." if triggered else "GOAL não corresponde aos gatilhos de Project Intelligence.",
    }
