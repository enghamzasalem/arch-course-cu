import json
from pathlib import Path
from typing import Dict, List, Optional
from ..models import Task
from .interfaces import ITaskStorage

class InMemoryTaskRepository(ITaskStorage):
    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
    def add(self, task: Task) -> None:
        self._tasks[task.id] = task
    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
    def list_all(self) -> List[Task]:
        return list(self._tasks.values())
    def update(self, task: Task) -> None:
        if task.id not in self._tasks:
            raise KeyError(f"Task {task.id} does not exist")
        self._tasks[task.id] = task
    def delete(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None
    def find_by_assignee(self, assignee: str) -> List[Task]:
        return [t for t in self._tasks.values() if t.assignee == assignee]

class FileTaskRepository(ITaskStorage):
    def __init__(self, path: Path) -> None:
        self._path = path
        self._tasks: Dict[str, Task] = {}
        self._load()
    def _load(self) -> None:
        if not self._path.exists():
            self._tasks = {}
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._tasks = {item["id"]: Task.from_dict(item) for item in raw}
    def _flush(self) -> None:
        self._path.write_text(json.dumps([t.to_dict() for t in self._tasks.values()], indent=2), encoding="utf-8")
    def add(self, task: Task) -> None:
        self._tasks[task.id] = task
        self._flush()
    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
    def list_all(self) -> List[Task]:
        return list(self._tasks.values())
    def update(self, task: Task) -> None:
        if task.id not in self._tasks:
            raise KeyError(f"Task {task.id} does not exist")
        self._tasks[task.id] = task
        self._flush()
    def delete(self, task_id: str) -> bool:
        ok = self._tasks.pop(task_id, None) is not None
        if ok:
            self._flush()
        return ok
    def find_by_assignee(self, assignee: str) -> List[Task]:
        return [t for t in self._tasks.values() if t.assignee == assignee]
