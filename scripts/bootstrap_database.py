from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]

DB = ROOT / "agentos" / "data" / "agentos.db"
DB.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    title TEXT,
    status TEXT,
    created_at TEXT,
    started_at TEXT,
    finished_at TEXT,
    executor TEXT,
    report TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS mission_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id TEXT,
    event TEXT,
    created_at TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS project_memory (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);
""")

conn.commit()
conn.close()

print("Banco criado:")
print(DB)
