from __future__ import annotations

import threading
import time
from copy import deepcopy
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Small dependency-free, thread-safe TTL cache for live URL feature results."""

    def __init__(self, ttl_seconds: int, max_entries: int = 2_000) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._items: dict[str, tuple[float, T]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> T | None:
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= time.monotonic():
                self._items.pop(key, None)
                return None
            return deepcopy(value)

    def set(self, key: str, value: T) -> None:
        with self._lock:
            if len(self._items) >= self.max_entries:
                oldest = next(iter(self._items))
                self._items.pop(oldest, None)
            self._items[key] = (time.monotonic() + self.ttl_seconds, deepcopy(value))
