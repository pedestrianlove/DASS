from __future__ import annotations

from collections.abc import Iterator

from app.core.config import get_settings
from app.db.session import SessionLocal


def get_db() -> Iterator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_worker_id() -> str:
    return get_settings().worker_id

