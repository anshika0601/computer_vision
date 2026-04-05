from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
LOGS_DIR = DATA_DIR / "logs"
ENCODINGS_PATH = DATA_DIR / "encodings.pkl"
DATABASE_PATH = DATA_DIR / "attendance.db"


def ensure_directories() -> None:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
