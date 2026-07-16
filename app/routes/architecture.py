from fastapi import APIRouter
from agentos.services.architecture_service import ArchitectureService

router = APIRouter(
    prefix="/admin",
    tags=["Architecture"],
)

@router.get("/architecture")
def architecture():
    return ArchitectureService().build()
