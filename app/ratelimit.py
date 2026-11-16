"""Limite simples de tentativas em memória (por processo).

Suficiente para uma instância única do Lunara. Se um dia rodar com vários
workers ou réplicas, trocar por Redis mantendo a mesma interface.
"""
from __future__ import annotations

import threading
import time
from collections import deque


class AttemptTracker:
    """Conta falhas por chave dentro de uma janela deslizante."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 900) -> None:
        self.max_attempts = max(1, max_attempts)
        self.window_seconds = max(1, window_seconds)
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        hits = self._hits.get(key)
        if hits is None:
            hits = deque()
            self._hits[key] = hits
        cutoff = now - self.window_seconds
        while hits and hits[0] < cutoff:
            hits.popleft()
        return hits

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, now)
            if not hits:
                self._hits.pop(key, None)
                return False
            return len(hits) >= self.max_attempts

    def register_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, now)
            hits.append(now)

    def clear(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)
