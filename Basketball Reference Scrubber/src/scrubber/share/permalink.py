"""Permalink encoding.

Two strategies, since this foundation has no web server of its own yet:

- ``encode_state``/``decode_state``/``build_permalink`` are fully
  stateless — the URL token *is* the state, compressed and base64'd, so
  any future server can resolve one without a database.
- ``PermalinkStore`` is an opt-in short-ID store (SQLite-backed) for when
  a stateless token is too long to be a nice URL. A future web layer can
  swap this for a real database without changing the call shape.
"""

from __future__ import annotations

import base64
import json
import sqlite3
import time
import uuid
import zlib
from typing import Any

from ..config import SETTINGS, Settings


def encode_state(state: dict[str, Any]) -> str:
    payload = json.dumps(state, separators=(",", ":"), sort_keys=True, default=str).encode("utf-8")
    compressed = zlib.compress(payload, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_state(token: str) -> dict[str, Any]:
    padding = "=" * (-len(token) % 4)
    compressed = base64.urlsafe_b64decode(token + padding)
    return json.loads(zlib.decompress(compressed))


def build_permalink(state: dict[str, Any], base_url: str = "https://bbref-scrubber.local") -> str:
    return f"{base_url.rstrip('/')}/p/{encode_state(state)}"


class PermalinkStore:
    def __init__(self, settings: Settings = SETTINGS):
        self.path = settings.cache_dir / "permalinks.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS permalinks (id TEXT PRIMARY KEY, state TEXT NOT NULL, created_at REAL NOT NULL)"
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def create(self, state: dict[str, Any]) -> str:
        short_id = uuid.uuid4().hex[:8]
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO permalinks (id, state, created_at) VALUES (?, ?, ?)",
                (short_id, json.dumps(state, default=str), time.time()),
            )
            conn.commit()
        return short_id

    def resolve(self, short_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT state FROM permalinks WHERE id = ?", (short_id,)).fetchone()
        return json.loads(row[0]) if row else None
