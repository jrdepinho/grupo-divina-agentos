import sqlite3

from agentos.core.settings import DATABASE_PATH


class MemoryStore:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)

    def set(self, key, value):

        self.conn.execute(
            """
            INSERT INTO project_memory(key,value,updated_at)
            VALUES(?,?,datetime('now'))
            ON CONFLICT(key)
            DO UPDATE SET
                value=excluded.value,
                updated_at=datetime('now')
            """,
            (key, value),
        )

        self.conn.commit()

    def get(self, key):

        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT value
            FROM project_memory
            WHERE key=?
            """,
            (key,),
        )

        row = cur.fetchone()

        if row:
            return row[0]

        return None

    def list(self):

        cur = self.conn.cursor()

        cur.execute(
            """
            SELECT
                key,
                value,
                updated_at
            FROM project_memory
            ORDER BY key
            """
        )

        return cur.fetchall()
