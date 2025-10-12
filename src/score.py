from __future__ import annotations
from pathlib import Path
import json
from typing import Any

# Save file lives next to this script (same folder as main.py)
BASE_DIR = Path(__file__).resolve().parent
SAVE_PATH = BASE_DIR / "score.json"

def _read_raw() -> dict:
    if SAVE_PATH.exists():
        try:
            return json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        except Exception:
            # If file is corrupted, reset
            return {"score": 0}
    return {"score": 0}

def _write_raw(data: dict) -> None:
    tmp = SAVE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
    tmp.replace(SAVE_PATH)

def load_score() -> int:
    """Return current score (defaults to 0)."""
    data = _read_raw()
    try:
        return int(data.get("score", 0))
    except Exception:
        return 0

def save_score(value: int) -> int:
    """Persist exact score value and return it."""
    _write_raw({"score": int(value)})
    return int(value)

def add_points(n: int = 1) -> int:
    """Add points (can be negative) and persist. Returns new score."""
    return save_score(load_score() + int(n))

def subtract_points(n: int = 1) -> int:
    """Subtract points and persist. Returns new score."""
    return add_points(-int(n))
