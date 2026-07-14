from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class GitService:

    def _run(self, *args):

        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        return result.stdout.strip()

    def status(self):
        return self._run("status", "--short")

    def current_branch(self):
        return self._run("branch", "--show-current")

    def branches(self):
        return self._run("branch")

    def log(self, limit=10):
        return self._run(
            "log",
            "--oneline",
            f"-{limit}",
        )

    def changed_files(self):
        return self._run(
            "diff",
            "--name-only",
        )


if __name__ == "__main__":

    svc = GitService()

    print("Branch:", svc.current_branch())
    print("Status:")
    print(svc.status())
