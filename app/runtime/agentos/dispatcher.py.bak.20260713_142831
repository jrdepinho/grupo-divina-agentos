from __future__ import annotations

from datetime import datetime
import traceback

from .registry import get


def execute(plan):

    report = {
        "ok": True,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "finished_at": None,
        "steps": [],
        "errors": [],
    }

    for index, step in enumerate(plan, start=1):

        action = step["action"]
        args = step.get("args", {})

        entry = {
            "index": index,
            "action": action,
            "args": args,
            "ok": False,
        }

        capability = get(action)

        if capability is None:

            entry["error"] = f"Capability '{action}' não encontrada."

            report["steps"].append(entry)
            report["errors"].append(entry)

            report["ok"] = False
            break

        try:

            result = capability.handler(**args)

            entry["ok"] = bool(result.get("ok", True))
            entry["result"] = result

            report["steps"].append(entry)

            if not entry["ok"]:

                report["errors"].append(entry)
                report["ok"] = False
                break

        except Exception as exc:

            entry["error"] = str(exc)
            entry["traceback"] = traceback.format_exc()

            report["steps"].append(entry)
            report["errors"].append(entry)

            report["ok"] = False
            break

    report["finished_at"] = datetime.utcnow().isoformat() + "Z"

    report["executed_steps"] = len(report["steps"])
    report["failed_steps"] = len(report["errors"])

    return report

