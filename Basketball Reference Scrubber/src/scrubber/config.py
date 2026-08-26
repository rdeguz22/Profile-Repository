from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CACHE_DIR = Path(os.environ.get("SCRUBBER_CACHE_DIR", str(_PROJECT_ROOT / ".cache")))


@dataclass(frozen=True)
class Settings:
    cache_dir: Path = _DEFAULT_CACHE_DIR
    cache_ttl_seconds: int = int(os.environ.get("SCRUBBER_CACHE_TTL", 60 * 60 * 24))
    request_timeout: float = float(os.environ.get("SCRUBBER_TIMEOUT", 30))
    max_retries: int = int(os.environ.get("SCRUBBER_MAX_RETRIES", 3))
    retry_backoff: float = float(os.environ.get("SCRUBBER_RETRY_BACKOFF", 1.5))


SETTINGS = Settings()
