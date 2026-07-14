
import uuid
from datetime import datetime

from agentos.core.database import connect


class MissionManager:

    def __init__(self):
        self.conn = connect()

    def now(self):
        return datetime.utcnow().isoformat()

    def event(self, mission_id, event):

        self.conn.execute(
            """
            INSERT INTO mission_events(
                mission_id,
                event,
                created_at
            )
            VALUES(?,?,?)
            """,
            (
                mission_id,
                event,
                self.now()
            )
        )

    def create(self, title, priority=100, depends_on=None):

        if depends_on is None:
            depends_on = []

        mission_id=str(uuid.uuid4())

        self.conn.execute(
            """
            INSERT INTO missions(
                id,title,status,created_at,priority
            )
            VALUES(?,?,?,?,?)
            """,
            (
                mission_id,
                title,
                "QUEUED",
                self.now(),
                priority
            )
        )

        for dep in depends_on:
            self.conn.execute(
                '''
                INSERT INTO mission_dependencies(
                    mission_id,
                    depends_on
                )
                VALUES(?,?)
                ''',
                (mission_id, dep)
            )

        self.event(mission_id,"CREATED")

        self.conn.commit()

        return mission_id

    def start(self, mission_id):

        self.conn.execute(
            """
            UPDATE missions
            SET
                status='RUNNING',
                started_at=?
            WHERE id=?
            """,
            (
                self.now(),
                mission_id
            )
        )

        self.event(mission_id,"STARTED")

        self.conn.commit()

    def finish(self, mission_id):

        self.conn.execute(
            """
            UPDATE missions
            SET
                status='DONE',
                finished_at=?
            WHERE id=?
            """,
            (
                self.now(),
                mission_id
            )
        )

        self.event(mission_id,"FINISHED")

        self.conn.commit()

    def fail(self, mission_id):

        self.conn.execute(
            """
            UPDATE missions
            SET
                status='FAILED',
                finished_at=?
            WHERE id=?
            """,
            (
                self.now(),
                mission_id
            )
        )

        self.event(mission_id,"FAILED")

        self.conn.commit()

    def list(self):

        cur=self.conn.cursor()

        cur.execute("""
            SELECT
                id,
                title,
                status,
                created_at
            FROM missions
            ORDER BY created_at DESC
        """)

        return cur.fetchall()

    def history(self, mission_id):

        cur=self.conn.cursor()

        cur.execute(
            """
            SELECT
                event,
                created_at
            FROM mission_events
            WHERE mission_id=?
            ORDER BY id
            """,
            (mission_id,)
        )

        return cur.fetchall()
