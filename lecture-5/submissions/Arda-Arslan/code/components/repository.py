import json
import os
from typing import Dict, List, Optional, Protocol
from models import Task


class ITaskRepository(Protocol):
    def add(self, task: Task) -> None:
        pass

    def get(self, task_id: str) -> Optional[Task]:
        pass

    def get_all(self) -> List[Task]:
        pass

    def update(self, task: Task) -> None:
        pass

    def delete(self, task_id: str) -> bool:
        pass


class InMemoryTaskRepository:
    # Simple repository, data stays only while program runs

    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add(self, task: Task):
        self.tasks[task.id] = task

    def get(self, task_id: str):
        return self.tasks.get(task_id)

    def get_all(self):
        return list(self.tasks.values())

    def update(self, task: Task):
        self.tasks[task.id] = task

    def delete(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False


class FileTaskRepository:
    # Stores tasks in a json file

    def __init__(self, file="tasks.json"):
        self.file = file
        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read(self):
        with open(self.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Task.from_dict(x) for x in data]

    def _write(self, tasks):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)

    def add(self, task: Task):
        tasks = self._read()
        tasks.append(task)
        self._write(tasks)

    def get(self, task_id):
        tasks = self._read()
        for t in tasks:
            if t.id == task_id:
                return t
        return None

    def get_all(self):
        return self._read()

    def update(self, task):
        tasks = self._read()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
        self._write(tasks)

    def delete(self, task_id):
        tasks = self._read()
        new = [t for t in tasks if t.id != task_id]

        if len(new) == len(tasks):
            return False

        self._write(new)
        return True