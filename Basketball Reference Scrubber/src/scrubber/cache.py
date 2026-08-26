from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class DiskCache:
    """A small SQLite-backed key/value cache with per-read TTL expiry.

    NBA Stats API responses are slow and rate-limited, so every read
    through NBAStatsClient is cached here first. TTL is passed at read
    time (not fixed at write time) so callers can tune freshness per
    request without needing separate cache instances.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def make_key(namespace: str, params: dict[str, Any]) -> str:
        payload = json.dumps({"namespace": namespace, "params": params}, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str, ttl_seconds: float) -> Any | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value, created_at FROM cache WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        value, created_at = row
        if time.time() - created_at > ttl_seconds:
            return None
        return json.loads(value)

    def set(self, key: str, value: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created_at) VALUES (?, ?, ?)",
                (key, json.dumps(value, default=str), time.time()),
            )

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cache")
