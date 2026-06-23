import json
import csv
from typing import List, Protocol
from models import Task


class ITaskExporter(Protocol):
    def export(self, tasks: List[Task], path: str):
        pass


class JsonExporter:
    # Exports tasks as json

    def export(self, tasks, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)


class CsvExporter:
    # Exports tasks as csv

    def export(self, tasks, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "status", "priority", "assignee"])

            for t in tasks:
                writer.writerow([t.id, t.title, t.status.value, t.priority.value, t.assignee])