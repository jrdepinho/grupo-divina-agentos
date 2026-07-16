from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agentos.developer import DeveloperEngine, list_capabilities


router = APIRouter(
    prefix="/admin/develop",
    tags=["Developer Engine"],
)

engine = DeveloperEngine()


class DeveloperAction(BaseModel):
    capability: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class Phase1Request(BaseModel):
    actions: list[DeveloperAction]


class Phase2Request(BaseModel):
    approved: bool = False
    actions: list[DeveloperAction]


@router.get("/capabilities")
def capabilities():
    return {"capabilities": list_capabilities()}


@router.post("/phase1")
def phase1(payload: Phase1Request):
    return engine.execute_phase1(
        [action.model_dump() for action in payload.actions]
    )


@router.post("/phase2")
def phase2(payload: Phase2Request):
    return engine.execute_phase2(
        [action.model_dump() for action in payload.actions],
        approved=payload.approved,
    )
