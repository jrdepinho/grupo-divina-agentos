from __future__ import annotations


def recover(step, result):

    action = step["action"]

    if action == "service.status":

        return [

            {
                "action": "service.restart",
                "args": {
                    "service": step["args"]["service"]
                }
            },

            {
                "action": "service.status",
                "args": {
                    "service": step["args"]["service"]
                }
            }

        ]

    return []
