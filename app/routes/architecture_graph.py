from fastapi import APIRouter

from agentos.services.architecture_graph import ArchitectureGraph

router = APIRouter(
    prefix="/admin",
    tags=["Architecture"],
)

@router.get("/architecture/graph")
def graph():
    return ArchitectureGraph().build()
