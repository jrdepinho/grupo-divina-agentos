from agentos.services.git_service import GitService
from agentos.services.project_inventory import ProjectInventory


class ArchitectureService:

    def build(self):

        git = GitService()
        inventory = ProjectInventory()

        return {
            "git": {
                "branch": git.current_branch(),
                "status": git.status(),
                "changed_files": git.changed_files(),
            },
            "inventory": inventory.scan(),
        }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            ArchitectureService().build(),
            indent=2
        )
    )
