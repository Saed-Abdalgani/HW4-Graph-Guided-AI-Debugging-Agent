"""Token-bucket style refill limits (RPM / TPM) for the gatekeeper."""

from __future__ import annotations

import threading
import time


class RefillBucket:
    """Fixed refill rate; supports blocking ``consume``."""

    def __init__(self, *, capacity: float, refill_per_second: float) -> None:
        if capacity <= 0 or refill_per_second <= 0:
            raise ValueError("capacity and refill_per_second must be positive")
        self._capacity = capacity
        self._refill = refill_per_second
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def _top_up(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last
        self._last = now
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill)

    def consume(self, amount: float, *, wait: bool = True) -> None:
        if amount <= 0:
            return
        while True:
            with self._lock:
                self._top_up()
                if self._tokens >= amount:
                    self._tokens -= amount
                    return
                deficit = amount - self._tokens
                wait_s = deficit / self._refill if self._refill else 0.05
            if not wait:
                raise RuntimeError("rate limit: insufficient tokens (non-blocking)")
            time.sleep(min(max(wait_s, 0.01), 2.0))


__all__ = ["RefillBucket"]
