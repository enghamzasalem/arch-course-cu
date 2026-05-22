"""
repository.py - TaskRepository components.

Single Responsibility: store and retrieve Task objects.

Two concrete implementations of ITaskStorage are provided here:
  - InMemoryTaskRepository  — stores tasks in a plain dict (no disk I/O).
  - FileTaskRepository      — persists tasks to a JSON file on disk.

Both satisfy the ITaskStorage protocol.  TaskManager never imports
either class directly; it receives whichever one is injected at startup.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from models import Task, TaskStatus, TaskPriority


# ---------------------------------------------------------------------------
# Helpers for JSON serialisation / deserialisation
# ---------------------------------------------------------------------------

def _task_to_dict(task: Task) -> dict:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "assignee_id": task.assignee_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "tags": task.tags,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


def _dict_to_task(d: dict) -> Task:
    return Task(
        task_id=d["task_id"],
        title=d["title"],
        description=d["description"],
        status=TaskStatus(d["status"]),
        priority=TaskPriority(d["priority"]),
        assignee_id=d.get("assignee_id"),
        due_date=datetime.fromisoformat(d["due_date"]) if d.get("due_date") else None,
        tags=d.get("tags", []),
        created_at=datetime.fromisoformat(d["created_at"]),
        updated_at=datetime.fromisoformat(d["updated_at"]),
    )


# ---------------------------------------------------------------------------
# Implementation 1: in-memory (no disk I/O — ideal for tests and demos)
# ---------------------------------------------------------------------------

class InMemoryTaskRepository:
    """Stores tasks in a dict.  Data is lost when the process exits."""

    def __init__(self) -> None:
        self._store: Dict[str, Task] = {}

    def save(self, task: Task) -> None:
        task.updated_at = datetime.utcnow()
        self._store[task.task_id] = task

    def get(self, task_id: str) -> Optional[Task]:
        return self._store.get(task_id)

    def delete(self, task_id: str) -> bool:
        if task_id in self._store:
            del self._store[task_id]
            return True
        return False

    def list_all(self) -> List[Task]:
        return list(self._store.values())


# ---------------------------------------------------------------------------
# Implementation 2: file-backed (persists to a JSON file on disk)
# ---------------------------------------------------------------------------

class FileTaskRepository:
    """
    Stores tasks as JSON on disk.
    Swapping InMemoryTaskRepository for this one requires zero changes to
    TaskManager — demonstrating the benefit of the ITaskStorage interface.
    """

    def __init__(self, file_path: str = "tasks.json") -> None:
        self._file_path = file_path
        if not os.path.exists(file_path):
            self._write({})

    # --- ITaskStorage interface methods ------------------------------------

    def save(self, task: Task) -> None:
        task.updated_at = datetime.utcnow()
        data = self._read()
        data[task.task_id] = _task_to_dict(task)
        self._write(data)

    def get(self, task_id: str) -> Optional[Task]:
        data = self._read()
        raw = data.get(task_id)
        return _dict_to_task(raw) if raw else None

    def delete(self, task_id: str) -> bool:
        data = self._read()
        if task_id in data:
            del data[task_id]
            self._write(data)
            return True
        return False

    def list_all(self) -> List[Task]:
        data = self._read()
        return [_dict_to_task(v) for v in data.values()]

    # --- Private helpers ---------------------------------------------------

    def _read(self) -> dict:
        with open(self._file_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, data: dict) -> None:
        with open(self._file_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
