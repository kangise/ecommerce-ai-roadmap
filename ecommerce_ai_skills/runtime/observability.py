"""Dependency-free request metrics and structured logging."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import Counter
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

from .errors import RateLimitError


class Metrics:
    """Process-local counters suitable for liveness and smoke monitoring.

    Durable business facts remain in SQLite/audit events. These counters are
    deliberately disposable and never presented as revenue or marketplace
    metrics.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Counter[str] = Counter()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self._counters.items()))


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line without serializing secrets."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            },
            ensure_ascii=False,
            sort_keys=True,
        )


class RateLimiter:
    """Small per-client fixed-window limiter for the embedded API.

    This is a safety floor for a single-process deployment, not a distributed
    quota system. A Postgres/Redis-backed limiter is still required for HA.
    """

    def __init__(self, limit_per_minute: int = 120):
        if limit_per_minute < 1:
            raise ValueError("limit_per_minute must be positive")
        self.limit = limit_per_minute
        self._lock = threading.Lock()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - 60.0
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.limit:
                retry_after = max(1, int(events[0] + 60.0 - now + 0.999))
                raise RateLimitError(retry_after=retry_after)
            events.append(now)
