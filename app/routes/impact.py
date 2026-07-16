from fastapi import APIRouter

from agentos.services.impact_analysis import ImpactAnalysisService

router = APIRouter(
    prefix="/admin",
    tags=["Impact"],
)

svc = ImpactAnalysisService()

@router.get("/impact")
def impact(target: str):
    return svc.analyze(target)
