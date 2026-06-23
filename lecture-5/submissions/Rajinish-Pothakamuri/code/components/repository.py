"""
Task Management System - Repository Component
"""

from __future__ import annotations

from typing import Dict, List, Optional, Protocol
import json
import os

from models import Task


class ITaskRepository(Protocol):
    """Interface for task storage."""

    def add(self, task: Task) -> None: ...
    def update(self, task: Task) -> None: ...
    def delete(self, task_id: str) -> None: ...
    def get(self, task_id: str) -> Optional[Task]: ...
    def list_all(self) -> List[Task]: ...


class InMemoryTaskRepository:
    """In-memory task storage."""

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self._tasks[task.id] = task

    def update(self, task: Task) -> None:
        self._tasks[task.id] = task

    def delete(self, task_id: str) -> None:
        if task_id in self._tasks:
            del self._tasks[task_id]

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        return list(self._tasks.values())


class FileTaskRepository:
    """JSON file-backed task storage."""

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        parent = os.path.dirname(self._file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if not os.path.exists(self._file_path):
            self._write([])

    def add(self, task: Task) -> None:
        tasks = self._read()
        tasks.append(task.to_dict())
        self._write(tasks)

    def update(self, task: Task) -> None:
        tasks = self._read()
        updated = False
        for i, data in enumerate(tasks):
            if data.get("id") == task.id:
                tasks[i] = task.to_dict()
                updated = True
                break
        if not updated:
            tasks.append(task.to_dict())
        self._write(tasks)

    def delete(self, task_id: str) -> None:
        tasks = self._read()
        tasks = [t for t in tasks if t.get("id") != task_id]
        self._write(tasks)

    def get(self, task_id: str) -> Optional[Task]:
        tasks = self._read()
        for data in tasks:
            if data.get("id") == task_id:
                return Task.from_dict(data)
        return None

    def list_all(self) -> List[Task]:
        return [Task.from_dict(d) for d in self._read()]

    def _read(self) -> List[dict]:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: List[dict]) -> None:
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
