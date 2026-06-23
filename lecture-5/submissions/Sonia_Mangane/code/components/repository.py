from typing import Protocol, List
import json
from enum import Enum
from datetime import datetime
from models import Task

class ITaskRepository(Protocol):
    """Interface for Task Storage"""
    def add(self, task: Task) -> None: ...
    def get_all(self) -> List[Task]: ...

class InMemoryTaskRepository:
    def __init__(self):
        self._tasks = []
    
    def add(self, task: Task):
        self._tasks.append(task)
        
    def get_all(self) -> List[Task]:
        return self._tasks

class FileTaskRepository:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename

    def add(self, task: Task):
        tasks = self.get_all()
        tasks.append(task)

        def clean_val(v):
            if isinstance(v, Enum):
                return v.name
            if isinstance(v, datetime):
                return v.isoformat()
            if isinstance(v, list):
                return [clean_val(item) for item in v]
            if isinstance(v, dict):
                return {k: clean_val(val) for k, val in v.items()}
            return v

        serializable_tasks = [
            {k: clean_val(v) for k, v in vars(t).items()}
            for t in tasks
        ]

        content = json.dumps(serializable_tasks, indent=4)

        with open(self.filename, "w") as f:
            f.write(content)

    def get_all(self) -> List[Task]:
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [Task(**d) for d in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []