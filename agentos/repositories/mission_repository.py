import json

from agentos.core.database import connect
from agentos.utils.time import now


class MissionRepository:

    def save_result(self, mission_id, result):
        conn = connect()
        try:
            conn.execute(
                """
                UPDATE missions
                SET result=?
                WHERE id=?
                """,
                (
                    json.dumps(result, ensure_ascii=False),
                    mission_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def finish(self, mission_id):
        conn = connect()

        try:
            conn.execute(
                """
                UPDATE missions
                SET
                    status='DONE',
                    finished_at=?,
                    last_heartbeat=NULL
                WHERE id=?
                """,
                (
                    now(),
                    mission_id,
                ),
            )

            conn.commit()

        finally:
            conn.close()

    def fail(self, mission_id, error):

        payload = json.dumps(error, ensure_ascii=False)

        conn = connect()

        try:
            conn.execute(
                """
                UPDATE missions
                SET
                    status='FAILED',
                    finished_at=?,
                    report=?,
                    result=?,
                    last_heartbeat=NULL
                WHERE id=?
                """,
                (
                    now(),
                    payload,
                    payload,
                    mission_id,
                ),
            )

            conn.commit()

        finally:
            conn.close()
