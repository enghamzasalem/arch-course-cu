#!/usr/bin/env python3
"""
Lecture 10 — Scalability (hot path)

Real-world scenario: CityBite "kitchen dashboard" — list active orders for a restaurant.

Anti-pattern: keep every order in one big list and scan it on every request → O(n) work
grows with *global* order volume, not with what this restaurant needs.

Better: index by restaurant_id so each query touches only local data → scales with
per-restaurant load (still tune DB indexes / caches in production).
"""

from __future__ import annotations

import random
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Order:
    order_id: str
    restaurant_id: str
    status: str


def make_orders(num_restaurants: int, orders_per_restaurant: int) -> list[Order]:
    rng = random.Random(42)
    orders: list[Order] = []
    for r in range(num_restaurants):
        rid = f"rest_{r}"
        for k in range(orders_per_restaurant):
            oid = f"ord_{r}_{k}"
            status = rng.choice(["PLACED", "COOKING", "READY", "PICKED_UP"])
            orders.append(Order(order_id=oid, restaurant_id=rid, status=status))
    rng.shuffle(orders)
    return orders


class NaiveOrderBoard:
    """All orders in one list — simple but does not scale with global catalog size."""

    def __init__(self, orders: list[Order]) -> None:
        self._orders = list(orders)

    def active_for_restaurant(self, restaurant_id: str) -> list[Order]:
        return [o for o in self._orders if o.restaurant_id == restaurant_id and o.status != "PICKED_UP"]


class IndexedOrderBoard:
    """Partition in memory by restaurant_id — same idea as DB partition key / index."""

    def __init__(self, orders: list[Order]) -> None:
        self._by_restaurant: dict[str, list[Order]] = defaultdict(list)
        for o in orders:
            self._by_restaurant[o.restaurant_id].append(o)

    def active_for_restaurant(self, restaurant_id: str) -> list[Order]:
        return [o for o in self._by_restaurant[restaurant_id] if o.status != "PICKED_UP"]


def bench(name: str, fn: Callable[[], None], repeat: int = 5) -> float:
    times: list[float] = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    avg = sum(times) / len(times)
    print(f"  {name}: avg {avg * 1000:.3f} ms (over {repeat} runs)")
    return avg


def main() -> None:
    restaurants = 500
    per_rest = 40  # 20k orders globally
    target = "rest_100"
    orders = make_orders(restaurants, per_rest)

    naive = NaiveOrderBoard(orders)
    indexed = IndexedOrderBoard(orders)

    def run_naive() -> None:
        naive.active_for_restaurant(target)

    def run_indexed() -> None:
        indexed.active_for_restaurant(target)

    print("CityBite — active orders for one restaurant (in-memory demo)\n")
    print(f"Dataset: {len(orders)} orders across {restaurants} restaurants\n")

    print("Query cost (single restaurant):")
    bench("Naive scan (full list)", run_naive)
    bench("Indexed by restaurant_id", run_indexed)

    n1 = len(naive.active_for_restaurant(target))
    n2 = len(indexed.active_for_restaurant(target))
    assert n1 == n2, (n1, n2)

    print("\nTakeaway: horizontal pod autoscaling helps only if each pod's *work per request*")
    print("does not grow with total system size — watch hot paths, indexes, and fan-out.")


if __name__ == "__main__":
    main()
