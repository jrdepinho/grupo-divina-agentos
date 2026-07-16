from fastapi import APIRouter
from agentos.services.git_service import GitService

router = APIRouter(
    prefix="/admin/git",
    tags=["Git"],
)

git = GitService()

@router.get("/status")
def status():
    return {
        "branch": git.current_branch(),
        "status": git.status(),
        "changed_files": git.changed_files(),
    }

@router.get("/branches")
def branches():
    return {
        "branches": git.branches().splitlines()
    }

@router.get("/log")
def log():
    return {
        "log": git.log(20).splitlines()
    }
