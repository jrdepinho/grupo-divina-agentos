import sqlite3

from agentos.core.settings import DATABASE_PATH


def connect():
    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn
