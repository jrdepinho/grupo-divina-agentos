from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agentos.developer.registry import (
    PHASE_1_CAPABILITIES,
    PHASE_2_CAPABILITIES,
    dispatch,
)


class DeveloperEngine:
    def execute_phase1(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        return self._execute(actions, PHASE_1_CAPABILITIES, phase="phase1")

    def execute_phase2(
        self,
        actions: list[dict[str, Any]],
        approved: bool,
    ) -> dict[str, Any]:
        if not approved:
            return {
                "status": "approval_required",
                "phase": "phase2",
                "results": [],
            }

        return self._execute(actions, PHASE_2_CAPABILITIES, phase="phase2")

    def _execute(
        self,
        actions: list[dict[str, Any]],
        allowed: set[str],
        phase: str,
    ) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        failed = False

        for index, action in enumerate(actions, start=1):
            capability = action.get("capability")
            arguments = action.get("arguments") or {}

            if capability not in allowed:
                results.append({
                    "index": index,
                    "capability": capability,
                    "success": False,
                    "error": f"Capacidade não permitida na {phase}.",
                })
                failed = True
                break

            try:
                data = dispatch(capability, arguments)
                success = bool(data.get("success", True))

                results.append({
                    "index": index,
                    "capability": capability,
                    "success": success,
                    "data": data,
                })

                if not success:
                    failed = True
                    break

            except Exception as exc:
                results.append({
                    "index": index,
                    "capability": capability,
                    "success": False,
                    "error": str(exc),
                })
                failed = True
                break

        return {
            "status": "failed" if failed else "completed",
            "phase": phase,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }
