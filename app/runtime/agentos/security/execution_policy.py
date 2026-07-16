from enum import Enum
from dataclasses import dataclass


class RiskLevel(str, Enum):
    READONLY = "readonly"
    SAFE = "safe"
    PRODUCTION = "production"


@dataclass
class CapabilityPolicy:
    name: str
    risk: RiskLevel
    requires_confirmation: bool


POLICIES = {
    "scan": CapabilityPolicy("scan", RiskLevel.READONLY, False),
    "context_build": CapabilityPolicy("context_build", RiskLevel.READONLY, False),
    "frontend_scan": CapabilityPolicy("frontend_scan", RiskLevel.READONLY, False),
    "backend_scan": CapabilityPolicy("backend_scan", RiskLevel.READONLY, False),
    "database_scan": CapabilityPolicy("database_scan", RiskLevel.READONLY, False),
    "memory_search": CapabilityPolicy("memory_search", RiskLevel.READONLY, False),

    "patch": CapabilityPolicy("patch", RiskLevel.SAFE, False),
    "compile": CapabilityPolicy("compile", RiskLevel.SAFE, False),
    "pytest": CapabilityPolicy("pytest", RiskLevel.SAFE, False),
    "git": CapabilityPolicy("git", RiskLevel.SAFE, False),

    "deploy": CapabilityPolicy("deploy", RiskLevel.PRODUCTION, True),
    "restart": CapabilityPolicy("restart", RiskLevel.PRODUCTION, True),
    "sql": CapabilityPolicy("sql", RiskLevel.PRODUCTION, True),
}


def get_policy(capability: str):
    return POLICIES.get(
        capability,
        CapabilityPolicy(capability, RiskLevel.PRODUCTION, True),
    )


from dataclasses import dataclass


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str | None = None


def evaluate(
    capability: str,
    approval: str = "auto",
):
    policy = get_policy(capability)

    approved = str(approval).strip().lower() in {
        "approved",
        "approve",
        "confirm",
        "confirmed",
        "confirmado",
        "autorizado",
        "yes",
        "sim",
    }

    if policy.requires_confirmation and not approved:
        return PolicyDecision(
            allowed=False,
            reason="requires_confirmation",
        )

    return PolicyDecision(
        allowed=True,
    )
