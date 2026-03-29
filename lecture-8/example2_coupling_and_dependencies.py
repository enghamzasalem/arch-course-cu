#!/usr/bin/env python3
"""
Example 2: Coupling styles — tight vs loose

Demonstrates:
- Direct dependency on concrete storage shape (data + implementation coupling)
- Layering: domain logic depends on an abstraction (port), not storage details
- Dependency direction: adapter implements the port

Reference: Chapter 8 — Compatibility and Coupling (Pautasso)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


class TightlyCoupledTaskService:
    """
    Service knows it is talking to an in-memory dict shaped like a table.
    Hard to swap storage; tests are tied to that structure.
    """

    def __init__(self) -> None:
        self._table: Dict[str, Dict[str, object]] = {}

    def create(self, task_id: str, title: str) -> None:
        self._table[task_id] = {"title": title, "done": False}

    def list_titles(self) -> List[str]:
        return [row["title"] for row in self._table.values()]


@dataclass
class Task:
    id: str
    title: str
    done: bool = False


class TaskRepository(ABC):
    """Port: domain depends only on this."""

    @abstractmethod
    def save(self, task: Task) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[Task]:
        pass


class InMemoryTaskRepository(TaskRepository):
    """Adapter: could be swapped for SQLite, HTTP API, etc."""

    def __init__(self) -> None:
        self._by_id: Dict[str, Task] = {}

    def save(self, task: Task) -> None:
        self._by_id[task.id] = task

    def list_all(self) -> List[Task]:
        return list(self._by_id.values())


class LooselyCoupledTaskService:
    """Depends on TaskRepository, not on dict keys or SQL."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def create(self, task_id: str, title: str) -> None:
        self._repo.save(Task(id=task_id, title=title))

    def list_titles(self) -> List[str]:
        return [t.title for t in self._repo.list_all()]


def main() -> None:
    print("=" * 60)
    print("Example 2: Coupling & dependency direction")
    print("=" * 60)

    tc = TightlyCoupledTaskService()
    tc.create("a", "Learn coupling")
    print("\nTightly coupled list:", tc.list_titles())

    repo: TaskRepository = InMemoryTaskRepository()
    lc = LooselyCoupledTaskService(repo)
    lc.create("b", "Learn compatibility")
    print("Loosely coupled list:", lc.list_titles())

    print("\nCoupling notes:")
    print("  • Tight: service ↔ concrete dict schema")
    print("  • Loose: service ↔ TaskRepository; storage is replaceable")
    print("=" * 60)


if __name__ == "__main__":
    main()
