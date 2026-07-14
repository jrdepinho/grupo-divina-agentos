from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    "main.py",
    "planner.py",
    "dispatcher.py",
    "executor.py",
    "worker.py",
    "api.py",
}

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    "backup",
    "backups",
    "logs",
    "tmp",
}

IGNORE_PREFIXES = (
    "app.backup",
)

class ProjectInventory:

    def _ignored(self, path: Path) -> bool:
        parts = path.parts

        for part in parts:
            if part in IGNORE_DIRS:
                return True

            for prefix in IGNORE_PREFIXES:
                if part.startswith(prefix):
                    return True

        return False

    def scan(self):

        inventory = {
            "root": str(ROOT),
            "files": {},
            "counts": {},
        }

        for target in TARGETS:

            found = []

            for p in ROOT.rglob(target):

                if self._ignored(p):
                    continue

                found.append(str(p.relative_to(ROOT)))

            found.sort()

            inventory["files"][target] = found
            inventory["counts"][target] = len(found)

        return inventory


if __name__ == "__main__":
    print(json.dumps(ProjectInventory().scan(), indent=2))
