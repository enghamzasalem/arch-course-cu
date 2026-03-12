"""
Task Repository Component

Responsible for storing and retrieving tasks.
Implements the Repository pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import json
from pathlib import Path

from models import Task


# ================================
# Interface
# ================================

class ITaskRepository(ABC):
    """Interface for task storage."""

    @abstractmethod
    def add(self, task: Task) -> None:
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        pass


# ================================
# Implementation 1
# ================================

class InMemoryTaskRepository(ITaskRepository):
    """
    Stores tasks in memory (list).
    Useful for testing.
    """

    def __init__(self):
        self.tasks: List[Task] = []

    def add(self, task: Task) -> None:
        self.tasks.append(task)

    def update(self, task: Task) -> None:
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                return

    def delete(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_by_id(self, task_id: str) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all(self) -> List[Task]:
        return self.tasks


# ================================
# Implementation 2
# ================================

class FileTaskRepository(ITaskRepository):
    """
    Stores tasks in a JSON file.
    """

    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.file_path.write_text("[]")

    def _read(self) -> List[dict]:
        return json.loads(self.file_path.read_text())

    def _write(self, data: List[dict]) -> None:
        self.file_path.write_text(json.dumps(data, indent=2))

    def add(self, task: Task) -> None:
        tasks = self._read()
        tasks.append(task.to_dict())
        self._write(tasks)

    def update(self, task: Task) -> None:
        tasks = self._read()
        for i, t in enumerate(tasks):
            if t["id"] == task.id:
                tasks[i] = task.to_dict()
        self._write(tasks)

    def delete(self, task_id: str) -> None:
        tasks = self._read()
        tasks = [t for t in tasks if t["id"] != task_id]
        self._write(tasks)

    def get_by_id(self, task_id: str) -> Optional[Task]:
        tasks = self._read()
        for t in tasks:
            if t["id"] == task_id:
                return Task(**t)
        return None

    def get_all(self) -> List[Task]:
        tasks = self._read()
        return [Task(**t) for t in tasks]