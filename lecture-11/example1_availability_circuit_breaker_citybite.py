#!/usr/bin/env python3
"""
Lecture 11 — Availability: circuit breaker (CityBite)

Real-world scenario: CityBite checkout calls an external **payment gateway**.
When the gateway is slow or failing, **blind retries** multiply load and can take down
your own API (cascading failure).

**Circuit breaker** — *What:* stop calling a sick dependency for a cooldown period;
fail fast or use a fallback. *Why:* protects **your** capacity; reduces **downstream**
call volume during their outage (Chapter 11 theme).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto


class CBState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


@dataclass
class FlakyPaymentGateway:
    failure_rate: float = 0.55
    rng: random.Random = field(default_factory=lambda: random.Random(7))
    call_count: int = 0

    def charge(self, order_id: str) -> str:
        self.call_count += 1
        if self.rng.random() < self.failure_rate:
            if self.rng.random() < 0.25:
                time.sleep(0.05)
            raise RuntimeError("gateway_error")
        return f"txn_ok:{order_id}"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    open_seconds: float = 0.35
    state: CBState = CBState.CLOSED
    consecutive_failures: int = 0
    opened_at: float = 0.0

    def call(self, gw: FlakyPaymentGateway, order_id: str) -> str:
        now = time.perf_counter()
        if self.state == CBState.OPEN:
            if now - self.opened_at >= self.open_seconds:
                self.state = CBState.HALF_OPEN
            else:
                raise RuntimeError("circuit_open_fail_fast")

        try:
            out = gw.charge(order_id)
        except Exception:
            self._on_failure(now)
            raise
        self._on_success()
        return out

    def _on_success(self) -> None:
        self.consecutive_failures = 0
        self.state = CBState.CLOSED

    def _on_failure(self, now: float) -> None:
        self.consecutive_failures += 1
        if self.state == CBState.HALF_OPEN:
            self.state = CBState.OPEN
            self.opened_at = now
            return
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CBState.OPEN
            self.opened_at = now


def run_naive_trials(gw: FlakyPaymentGateway, trials: int) -> tuple[int, int]:
    """Up to 5 retries per checkout — counts total gateway invocations."""
    successes = 0
    for _ in range(trials):
        last: Exception | None = None
        for _ in range(5):
            try:
                gw.charge("ORD-123")
                successes += 1
                break
            except Exception as e:
                last = e
        else:
            if last:
                pass  # failed after retries
    return successes, gw.call_count


def run_cb_trials(gw: FlakyPaymentGateway, cb: CircuitBreaker, trials: int) -> tuple[int, int]:
    successes = 0
    for _ in range(trials):
        try:
            cb.call(gw, "ORD-123")
            successes += 1
        except Exception:
            pass
    return successes, gw.call_count


def main() -> None:
    trials = 60
    print("CityBite — payment gateway under stress\n")
    print(f"{trials} checkout attempts each mode.\n")

    gw1 = FlakyPaymentGateway()
    ok1, calls1 = run_naive_trials(gw1, trials)
    print(f"Naive (up to 5 retries each checkout):")
    print(f"  Checkouts succeeded: {ok1}/{trials}")
    print(f"  Total gateway calls: {calls1}  ← retries multiply load on a sick partner\n")

    gw2 = FlakyPaymentGateway()
    cb = CircuitBreaker()
    ok2, calls2 = run_cb_trials(gw2, cb, trials)
    print(f"With circuit breaker:")
    print(f"  Checkouts succeeded: {ok2}/{trials}")
    print(f"  Total gateway calls: {calls2}  ← fewer calls while OPEN = less pile-on")
    print("  (Success rate drops unless you add async pay / queue / cached idempotency — that is the product trade.)\n")

    print("Takeaway: breakers shed work to protect both sides; pair with timeouts,")
    print("bulkheads, and honest degraded UX when pay-now is unsafe.")


if __name__ == "__main__":
    main()
