import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
BASE_DIR = Path(__file__).resolve().parents[1]
raw_db = os.getenv("DATABASE_PATH", "./data/querygpt.db")
DATABASE_PATH = (BASE_DIR / raw_db).resolve() if not Path(raw_db).is_absolute() else Path(raw_db)
MAX_RESULT_ROWS = max(1, min(int(os.getenv("MAX_RESULT_ROWS", "500")), 5000))
QUERY_TIMEOUT_SECONDS = max(1, min(int(os.getenv("QUERY_TIMEOUT_SECONDS", "3")), 10))
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
