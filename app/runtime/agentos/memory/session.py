from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_SESSIONS: dict[str, 'ExecutionSession'] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutionSession:
    goal: str
    mode: str = "execute"
    approval: str = "auto"
    risk_limit: str = "normal"
    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    plan: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] | None = None

    def add_event(
        self,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        self.events.append(
            {
                "at": utc_now(),
                "type": event_type,
                "data": data,
            }
        )

    def finish(self) -> None:
        self.finished_at = utc_now()
        _SESSIONS[self.session_id] = self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_session(session_id: str):
    return _SESSIONS.get(session_id)


def save_session(session: ExecutionSession):
    _SESSIONS[session.session_id] = session
