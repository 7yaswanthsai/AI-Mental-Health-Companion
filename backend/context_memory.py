from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict, List, Optional

from database.db_connection import get_database

try:
    _db = get_database()
    _context_collection = _db["chat_context"]
except Exception:  # pragma: no cover
    _context_collection = None

_memory_cache: Dict[str, Deque[dict]] = defaultdict(lambda: deque(maxlen=5))


def _make_record(subject_id: str, user_msg: str, bot_msg: str, metadata: Optional[dict]) -> dict:
    return {
        "subject_id": subject_id,
        "user": user_msg,
        "bot": bot_msg,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow(),
    }


def append_context(subject_id: str, user_msg: str, bot_msg: str, metadata: Optional[dict] = None) -> None:
    record = _make_record(subject_id, user_msg, bot_msg, metadata)
    cache = _memory_cache[subject_id]
    cache.append(record)

    if _context_collection is not None:
        try:
            _context_collection.insert_one(record, max_time_ms=2000)
        except Exception:  # pragma: no cover
            # MongoDB unavailable - continue with in-memory cache only
            pass


def get_context(subject_id: str, limit: int = 5) -> List[dict]:
    history: List[dict] = list(_memory_cache.get(subject_id, []))

    if not history and _context_collection is not None:
        try:
            cursor = (
                _context_collection.find({"subject_id": subject_id}, max_time_ms=2000)
                .sort("timestamp", -1)
                .limit(limit)
            )
            history = list(cursor)[::-1]  # oldest first
            for item in history:
                item.pop("_id", None)
            _memory_cache[subject_id] = deque(history, maxlen=limit)
        except Exception:  # pragma: no cover
            # MongoDB unavailable - use in-memory cache only
            history = list(_memory_cache.get(subject_id, []))

    return history[-limit:]

