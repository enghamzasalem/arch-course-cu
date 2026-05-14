#!/usr/bin/env python3
"""
CityBite — API evolution: additive vs breaking JSON (Lecture 12).

Run: python3 example2_flexibility_api_evolution_citybite.py

No HTTP server: pure dict payloads show compatibility rules from the lecture.
"""

from __future__ import annotations

import json
from typing import Any


def order_v1(order_id: str, total_cents: int, status: str) -> dict[str, Any]:
    """Original public shape — old mobile clients depend on these keys only."""
    return {"orderId": order_id, "totalCents": total_cents, "status": status}


def order_v1_additive(order_id: str, total_cents: int, status: str) -> dict[str, Any]:
    """
    Additive change: new optional field; old clients ignore unknown keys.
    Safe if clients use tolerant JSON parsers (typical).
    """
    base = order_v1(order_id, total_cents, status)
    base["estimatedDeliveryMinutes"] = 42  # optional enhancement
    return base


def order_v2_breaking_rename(order_id: str, total_cents: int, status: str) -> dict[str, Any]:
    """
    Breaking change: renamed field — old clients looking for 'orderId' break.
    Requires coordinated rollout or explicit /v2 + deprecation window.
    """
    return {"id": order_id, "total_cents": total_cents, "state": status}


def simulate_old_client(payload: dict[str, Any]) -> str:
    """Old client only reads documented v1 keys."""
    oid = payload.get("orderId")
    total = payload.get("totalCents")
    st = payload.get("status")
    return f"display order={oid} total={total} status={st}"


def main() -> None:
    o1 = order_v1("o1", 1299, "PLACED")
    o1a = order_v1_additive("o1", 1299, "PLACED")
    o2 = order_v2_breaking_rename("o1", 1299, "PLACED")

    print("v1:", json.dumps(o1))
    print("old client + v1:", simulate_old_client(o1))
    print()
    print("v1 additive:", json.dumps(o1a))
    print("old client + additive:", simulate_old_client(o1a))
    print()
    print("v2 breaking:", json.dumps(o2))
    print("old client + v2 (broken):", simulate_old_client(o2))
    print(
        "\nLesson: prefer additive fields + deprecation; "
        "if you must break, ship /v2 or version header and sunset v1 with dates."
    )


if __name__ == "__main__":
    main()
