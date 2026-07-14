import json
import sqlite3
import uuid
from datetime import datetime, UTC

from agentos.core.settings import DATABASE_PATH


class AdminService:

    @staticmethod
    def enqueue(operation, payload=None, priority=100):

        conn = sqlite3.connect(DATABASE_PATH)

        mission_id = str(uuid.uuid4())

        conn.execute("""
        INSERT INTO missions (
            id,
            status,
            type,
            payload,
            priority,
            created_at
        )
        VALUES (?,?,?,?,?,?)
        """,(
            mission_id,
            "QUEUED",
            "admin",
            json.dumps({
                "operation": operation,
                **(payload or {})
            }),
            priority,
            datetime.now(UTC).isoformat()
        ))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "mission_id": mission_id
        }
