#!/usr/bin/env python3
"""
Lecture 10 — Scalability (throughput / decoupling)

Real-world scenario: CityBite sends "order confirmed" push notifications and emails
after checkout. Doing all outbound calls *inside* the HTTP request slows checkout and
limits how many orders/sec one process can accept.

Better: enqueue lightweight events; worker pool drains the queue — classic way to
absorb spikes (dinner rush) and scale consumers independently from the API tier.

This script uses threads + a pool to model parallel workers (I/O waits release the GIL).
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, wait


def simulate_external_notify(_order_id: str) -> None:
    """Pretend SMS/push gateway latency."""
    time.sleep(0.002)


def checkout_synchronous(num_orders: int) -> float:
    """Anti-pattern: do slow side effects before responding to client."""
    t0 = time.perf_counter()
    for i in range(num_orders):
        simulate_external_notify(f"ORD-{i}")
    return time.perf_counter() - t0


def checkout_with_worker_pool(num_orders: int, workers: int) -> tuple[float, float]:
    """
    Accept phase: only build list (instant vs network — represents enqueue after DB write).
    Drain phase: thread pool runs notifies in parallel (models N workers / async I/O).
    """
    accept_start = time.perf_counter()
    order_ids = [f"ORD-{i}" for i in range(num_orders)]
    accept_dt = time.perf_counter() - accept_start

    drain_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(simulate_external_notify, oid) for oid in order_ids]
        wait(futures)
    drain_dt = time.perf_counter() - drain_start
    return accept_dt, drain_dt


def main() -> None:
    n = 200
    workers = 8

    print("CityBite — notify customers after checkout\n")
    print(f"Simulate {n} checkouts; each notify ~2 ms (I/O bound)\n")

    t_sync = checkout_synchronous(n)
    t_accept, t_drain = checkout_with_worker_pool(n, workers=workers)

    print(f"Synchronous (notify inside request): {t_sync * 1000:.1f} ms total")
    print(f"  → checkout latency includes ALL {n} notifies — user waits.\n")

    print(f"Enqueue + {workers} parallel workers (thread pool model):")
    print(f"  Accept / enqueue phase:           {t_accept * 1000:.3f} ms")
    print(f"  Drain notifications (parallel):    {t_drain * 1000:.1f} ms")
    print("  → HTTP handler can return after persist+enqueue; workers catch up.\n")

    print("Takeaway: separate *ingress* throughput from *downstream* throughput;")
    print("use queues, autoscaling workers, and backpressure policies for dinner rush.")


if __name__ == "__main__":
    main()
