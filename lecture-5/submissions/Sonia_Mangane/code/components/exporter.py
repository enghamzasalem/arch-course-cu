from datetime import datetime
from typing import Protocol, List
import json
import csv
from enum import Enum
from models import Task

class ITaskExporter(Protocol):
    """Interface for Exporting Data"""
    def export(self, tasks: List[Task], path: str) -> None: ...

class JsonExporter:
    def export(self, tasks, path: str):
        # We create a helper to convert Enums to strings during export
        def data_cleaner(obj):
            if isinstance(obj, Enum):
                return obj.name  # Converts TaskPriority.HIGH to "HIGH"
            if isinstance(obj, datetime):
                return obj.isoformat()  # Converts datetime to ISO string
            return obj

        # Apply a deeper cleaning to the task dictionaries
        cleaned_tasks = []
        for t in tasks:
            task_dict = vars(t)
            # Ensure every value in the dict is JSON-safe
            safe_dict = {k: data_cleaner(v) for k, v in task_dict.items()}
            cleaned_tasks.append(safe_dict)

        with open(path, 'w') as f:
            json.dump(cleaned_tasks, f, indent=4)
        print(f"Successfully exported to {path}")

class CsvExporter:
    def export(self, tasks: List[Task], path: str):
        if not tasks: return
        keys = vars(tasks[0]).keys()
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows([vars(t) for t in tasks])
        print(f"Exported to CSV at {path}")