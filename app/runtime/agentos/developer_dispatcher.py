from __future__ import annotations

from typing import Any

from agentos.developer.engine import DeveloperEngine


ACTION_MAP = {
    "developer.write": "code.write_file",
    "developer.patch": "code.patch_file",
    "developer.compile": "python.compile",
    "developer.validate": "tests.run",
}


class DeveloperDispatcher:

    def __init__(self):
        self.engine = DeveloperEngine()

    def normalize(self, actions: list[dict[str, Any]]):

        converted = []

        for item in actions:

            action = item.get("action")
            capability = ACTION_MAP.get(action)

            if capability is None:
                continue

            converted.append(
                {
                    "capability": capability,
                    "arguments": item.get("args", {}),
                }
            )

        return converted

    def phase1(self, actions):
        return self.engine.execute_phase1(
            self.normalize(actions)
        )

    def phase2(self, actions, approved=True):
        return self.engine.execute_phase2(
            self.normalize(actions),
            approved,
        )
