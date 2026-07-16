from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

IGNORE = {
    ".git",
    "venv",
    "__pycache__",
    "backup",
    "backups",
    "logs",
    "tmp",
}

PREFIXES = (
    "app.backup",
)

class DependencyService:

    def ignored(self, path: Path):

        for part in path.parts:

            if part in IGNORE:
                return True

            for prefix in PREFIXES:
                if part.startswith(prefix):
                    return True

        return False

    def build(self):

        graph = {}

        for file in ROOT.rglob("*.py"):

            if self.ignored(file):
                continue

            try:

                tree = ast.parse(file.read_text(encoding="utf-8"))

            except Exception:
                continue

            imports = []

            for node in ast.walk(tree):

                if isinstance(node, ast.Import):

                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):

                    if node.module:
                        imports.append(node.module)

            graph[str(file.relative_to(ROOT))] = sorted(set(imports))

        return graph


if __name__ == "__main__":

    import json

    print(json.dumps(DependencyService().build(), indent=2))
