from fastapi import APIRouter
from agentos.services.project_inventory import ProjectInventory

router = APIRouter(
    prefix="/admin/project",
    tags=["Project Inventory"],
)

@router.get("/inventory")
def inventory():
    return ProjectInventory().scan()
