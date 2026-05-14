#!/usr/bin/env python3
"""
Example 1: Compatibility and API evolution

Demonstrates:
- Syntactic vs semantic compatibility (payload shape vs meaning)
- Backward-compatible extension (optional fields, additive response keys)
- Breaking change (renaming/removing required fields)
- Semantic versioning mindset: what forces MAJOR vs MINOR

Reference: Chapter 8 — Compatibility and Coupling (Pautasso)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ChangeKind(Enum):
    """Rough classification of API changes."""

    ADDITIVE_OPTIONAL_FIELD = "non_breaking_minor"
    ADDITIVE_RESPONSE_KEY = "non_breaking_minor"
    REMOVE_REQUIRED_FIELD = "breaking_major"
    RENAME_FIELD = "breaking_major"
    TIGHTEN_VALIDATION = "often_breaking_semantic"


@dataclass
class TaskV1:
    """Client-facing task as of API v1."""

    id: str
    title: str
    done: bool


@dataclass
class TaskV2:
    """v2 adds optional metadata — old clients can ignore unknown keys."""

    id: str
    title: str
    done: bool
    priority: Optional[str] = None  # "low" | "med" | "high"


def task_to_json_v1(task: TaskV1) -> str:
    return json.dumps(asdict(task), sort_keys=True)


def task_to_json_v2(task: TaskV2) -> str:
    d = asdict(task)
    d = {k: v for k, v in d.items() if v is not None}
    return json.dumps(d, sort_keys=True)


def parse_task_lenient(payload: Dict[str, Any]) -> TaskV2:
    """
    Lenient server: unknown keys ignored, missing optional fields defaulted.
    Helps backward compatibility when clients send partial or older shapes.
    """
    return TaskV2(
        id=str(payload["id"]),
        title=str(payload["title"]),
        done=bool(payload["done"]),
        priority=payload.get("priority"),
    )


class LegacyClient:
    """Simulates a client compiled against v1 — only knows id, title, done."""

    def display(self, response_json: str) -> str:
        data = json.loads(response_json)
        t = TaskV1(id=data["id"], title=data["title"], done=data["done"])
        return f"[v1 client] {t.id}: {t.title} done={t.done}"


def classify_change(description: str, kind: ChangeKind) -> None:
    print(f"  {description}")
    print(f"    → {kind.value}")


def main() -> None:
    print("=" * 60)
    print("Example 1: Compatibility & API evolution")
    print("=" * 60)

    print("\n--- Change classification (conceptual) ---")
    classify_change(
        "Add optional query param `?expand=comments` with default off",
        ChangeKind.ADDITIVE_OPTIONAL_FIELD,
    )
    classify_change(
        "Add new JSON field `priority` (optional) in response",
        ChangeKind.ADDITIVE_RESPONSE_KEY,
    )
    classify_change(
        "Remove required field `title` from request body",
        ChangeKind.REMOVE_REQUIRED_FIELD,
    )
    classify_change(
        "Rename `done` → `completed` without alias",
        ChangeKind.RENAME_FIELD,
    )
    classify_change(
        "Start rejecting titles shorter than 3 chars (was allowed)",
        ChangeKind.TIGHTEN_VALIDATION,
    )

    print("\n--- Same logical task, v1 vs v2 JSON ---")
    t1 = TaskV1(id="1", title="Buy milk", done=False)
    t2 = TaskV2(id="1", title="Buy milk", done=False, priority="high")
    print("v1:", task_to_json_v1(t1))
    print("v2:", task_to_json_v2(t2))

    print("\n--- Legacy client reading v2 response ---")
    client = LegacyClient()
    print(client.display(task_to_json_v2(t2)))

    print("\n--- Lenient server parsing older client body ---")
    old_body = {"id": "2", "title": "Walk dog", "done": True}
    print("Parsed:", task_to_json_v2(parse_task_lenient(old_body)))

    print("\nKey idea: preserve old clients by additive, optional evolution; ")
    print("document semantic changes even when JSON shape stays the same.")
    print("=" * 60)


if __name__ == "__main__":
    main()
