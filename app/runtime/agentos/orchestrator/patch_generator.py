from __future__ import annotations


class PatchGenerator:

    def generate(
        self,
        goal,
        candidates,
    ):

        if not candidates:
            return []

        return [
            {
                "action":"developer.read",
                "args":{
                    "path":candidates[0].path
                },
            },
            {
                "action":"developer.patch",
                "args":{
                    "path":candidates[0].path,
                    "goal":goal,
                },
            },
        ]
