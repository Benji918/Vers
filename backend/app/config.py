import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory or project root
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = str(BASE_DIR / "data" / "db" / "web.sqlite")

DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")
DATABASE_PATH = os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)
DEEPGRAM_MODEL = os.environ.get("DEEPGRAM_MODEL", "nova-3")
ENDPOINTING_MS = int(os.environ.get("ENDPOINTING_MS", "500"))
UTTERANCE_END_MS = int(os.environ.get("UTTERANCE_END_MS", "1000"))
