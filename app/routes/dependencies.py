from fastapi import APIRouter
from agentos.services.dependency_service import DependencyService

router = APIRouter(
    prefix="/admin",
    tags=["Dependencies"],
)

@router.get("/dependencies")
def dependencies():
    return DependencyService().build()
