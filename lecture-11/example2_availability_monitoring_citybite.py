#!/usr/bin/env python3
"""
Lecture 11 — Availability: monitoring probes (CityBite)

Real-world scenario: Kubernetes (from Lecture 9) uses **liveness** vs **readiness**
probes. A process can be "up" but unable to serve (DB pool exhausted, deadlock).

This script contrasts:
- **Shallow probe** — process answered "OK" on /healthz
- **Deep probe** — cheap dependency check (here: "can we acquire DB-like resource?")

*What:* observability distinguishes "running binary" from "useful service".
*Why:* routing traffic only when **ready** avoids piling load onto a half-dead pod
(lect11: active watchdog vs meaningful probe).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class FakeDBPool:
    max_connections: int = 3
    in_use: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def try_acquire(self, timeout: float = 0.01) -> bool:
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            with self.lock:
                if self.in_use < self.max_connections:
                    self.in_use += 1
                    return True
            time.sleep(0.001)
        return False

    def release(self) -> None:
        with self.lock:
            self.in_use = max(0, self.in_use - 1)


def shallow_health() -> bool:
    """HTTP 200 if Python process is alive — does not prove checkout will work."""
    return True


def deep_readiness(pool: FakeDBPool) -> bool:
    """Fails if we cannot get a connection — closer to "can take an order now"."""
    if pool.try_acquire(0.02):
        pool.release()
        return True
    return False


def main() -> None:
    pool = FakeDBPool(max_connections=2)
    # Simulate leak / stuck handlers: hold all pool slots
    assert pool.try_acquire(1)
    assert pool.try_acquire(1)

    print("CityBite — Order API pod under DB pool exhaustion\n")
    print(f"Pool: max={pool.max_connections}, all slots held (simulated stuck requests).\n")

    print(f"  Shallow /healthz style: {shallow_health()}  ← load balancer might still send traffic")
    print(f"  Deep readiness (try acquire): {deep_readiness(pool)}  ← should NOT get new sessions\n")

    pool.release()
    pool.release()
    print("After releasing pool:")
    print(f"  Deep readiness: {deep_readiness(pool)}\n")

    print("Takeaway: define **SLIs** on user-visible success; readiness should track **critical**")
    print("dependencies — not only `return 200` from an empty handler.")


if __name__ == "__main__":
    main()
