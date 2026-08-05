from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class RateLimitResult:
    allowed: bool
    retry_after: int


_ATTEMPTS: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str, *, limit: int = 5, window_seconds: int = 60) -> RateLimitResult:
    now = monotonic()
    bucket = _ATTEMPTS[key]
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        retry_after = max(1, int(window_seconds - (now - bucket[0])))
        return RateLimitResult(False, retry_after)
    bucket.append(now)
    return RateLimitResult(True, 0)
