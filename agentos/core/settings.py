from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

AGENTOS_DIR = ROOT_DIR / "agentos"
DATA_DIR = AGENTOS_DIR / "data"

MISSION_DIR = ROOT_DIR / "missions"

DATABASE_PATH = DATA_DIR / "agentos.db"

LOG_DIR = ROOT_DIR / "logs"

REPORT_DIR = MISSION_DIR / "reports"
QUEUE_DIR = MISSION_DIR / "queue"
RUNNING_DIR = MISSION_DIR / "running"
COMPLETED_DIR = MISSION_DIR / "completed"
FAILED_DIR = MISSION_DIR / "failed"
