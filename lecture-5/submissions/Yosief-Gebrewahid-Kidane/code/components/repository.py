"""
Task Repository Component
Handles persistence of tasks.
"""

from typing import Dict, List, Optional, Protocol
from models import Task


class ITaskRepository(Protocol):
    """Repository interface for tasks."""

    def add(self, task: Task) -> None:
        ...

    def get(self, task_id: str) -> Optional[Task]:
        ...

    def list(self) -> List[Task]:
        ...

    def delete(self, task_id: str) -> None:
        ...


class InMemoryTaskRepository:
    """Simple in-memory repository implementation."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list(self) -> List[Task]:
        return list(self.tasks.values())

    def delete(self, task_id: str) -> None:
        if task_id in self.tasks:
            del self.tasks[task_id]


class FileTaskRepository:

    def __init__(self, filepath):
        self.filepath = filepath

    def add(self, task):
        # logic to save task to file
        pass

    def get(self, task_id):
        # logic to retrieve task from file
        pass

    def list(self):
        # logic to read tasks from file
        pass

    def delete(self, task_id):
        # logic to delete task from file
        pass
