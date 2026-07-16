from __future__ import annotations

from datetime import datetime, UTC
from inspect import signature, Parameter
import traceback

from app.runtime.agentos.registry import get
from app.runtime.agentos.bootstrap import initialize


class DispatcherV2:

    def execute(self, plan):

        initialize()

        report = {
            "ok": True,
            "started_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "finished_at": None,
            "steps": [],
            "errors": [],
            "pipeline_context": {},
        }

        pipeline_context = report["pipeline_context"]

        for step in plan:

            action = step["action"]

            args = {
                **pipeline_context,
                **step.get("args", {}),
            }

            action = step.get("action", "")

            # Injeta automaticamente o primeiro arquivo encontrado
            if action == "developer.read":
                matches = pipeline_context.get("matches", [])
                if matches:
                    args.setdefault("path", matches[0])
                else:
                    report["steps"].append({
                        **step,
                        "args": args,
                        "ok": True,
                        "skipped": True,
                        "reason": "Nenhum arquivo encontrado pelo developer.search"
                    })
                    continue

            # Patch também precisa de um path
            if action == "developer.patch":
                matches = pipeline_context.get("matches", [])
                if matches:
                    args.setdefault("path", matches[0])


            entry = {
                "order": step.get("order"),
                "action": action,
                "metadata": step.get("metadata"),
                "args": args,
                "ok": False,
            }

            capability = get(action)

            if capability is None:
                entry["error"] = (
                    f"Capability '{action}' não encontrada."
                )
                report["steps"].append(entry)
                report["errors"].append(entry)
                report["ok"] = False
                break

            try:

                handler = capability.handler

                sig = signature(handler)

                accepts_kwargs = any(
                    p.kind == Parameter.VAR_KEYWORD
                    for p in sig.parameters.values()
                )

                if accepts_kwargs:
                    call_args = args
                else:
                    call_args = {
                        k: v
                        for k, v in args.items()
                        if k in sig.parameters
                    }

                result = handler(**call_args)

                if result is None:
                    result = {}

                if not isinstance(result, dict):
                    result = {
                        "value": result,
                    }

                # Compartilha apenas dados úteis entre as capabilities.
                exported = {
                    k: v
                    for k, v in result.items()
                    if k in {
                        "matches",
                        "match",
                        "path",
                        "paths",
                        "content",
                        "contents",
                        "stdout",
                        "stderr",
                        "context",
                        "data",
                    }
                }

                pipeline_context.update(exported)

                entry["ok"] = bool(result.get("ok", True))
                entry["result"] = result

                report["steps"].append(entry)

                if (
                    action == "service.restart"
                    and args.get("service")
                    == "agente-divina-api.service"
                    and entry["ok"]
                ):
                    report["finished_at"] = (
                        datetime.now(UTC).isoformat().replace("+00:00", "Z")
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

        report["finished_at"] = (
            datetime.now(UTC).isoformat().replace("+00:00", "Z")
        )

        report["executed_steps"] = len(report["steps"])
        report["failed_steps"] = len(report["errors"])

        return report
