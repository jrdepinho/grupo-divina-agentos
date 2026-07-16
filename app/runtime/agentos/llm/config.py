import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[4]

ENV_FILE = ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "auto",
).lower()

LLM_MODEL_OPENAI = os.getenv(
    "LLM_MODEL_OPENAI",
    "gpt-5.5",
)

LLM_MODEL_OPENROUTER = os.getenv(
    "LLM_MODEL_OPENROUTER",
    "openai/gpt-4.1-mini",
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
)
