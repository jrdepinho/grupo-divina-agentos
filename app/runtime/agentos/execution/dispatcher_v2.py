from __future__ import annotations

from datetime import datetime
import traceback

from app.runtime.agentos.registry import get
from app.runtime.agentos.security.execution_policy import get_policy


class DispatcherV2:

    def execute(self, plan, session=None):

        report = {
            "ok": True,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "steps": [],
            "errors": [],
        }

        for step in plan:

            if session:
                session.add_event(
                    "step.started",
                    {
                        "action": step["action"],
                        "order": step.get("order"),
                    },
                )


            action = step["action"]
            args = step.get("args", {})

            entry = {
                "order": step.get("order"),
                "action": action,
                "metadata": step.get("metadata"),
                "args": args,
                "ok": False,
            }

            capability = get(action)

            policy = get_policy(action)

            entry["policy"] = {
                "name": policy.name,
                "risk": policy.risk.value,
                "requires_confirmation": policy.requires_confirmation,
            }

            if capability is None:
                entry["error"] = f"Capability '{action}' não encontrada."
                report["steps"].append(entry)

                if session:
                    session.add_event(
                        "step.finished",
                        {
                            "action": action,
                            "ok": entry["ok"],
                        },
                    )
                report["errors"].append(entry)
                report["ok"] = False
                break

            try:
                result = capability.handler(**args)

                entry["ok"] = bool(result.get("ok", True))
                entry["result"] = result

                report["steps"].append(entry)

                # Restart do próprio serviço encerra a execução.
                if (
                    action == "service.restart"
                    and args.get("service") == "agente-divina-api.service"
                    and entry["ok"]
                ):
                    report["finished_at"] = (
                        datetime.utcnow().isoformat() + "Z"
                    )
                    report["executed_steps"] = len(report["steps"])
                    report["failed_steps"] = len(report["errors"])
                    report["restart_in_progress"] = True
                    return report

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
