"""
Task Exporter Component
Responsible for exporting tasks to different formats.
"""

from typing import List, Protocol
import json
import csv
from models import Task


class ITaskExporter(Protocol):
    """Exporter interface."""

    def export(self, tasks: List[Task], filepath: str) -> None:
        ...


class JsonExporter:
    """Exports tasks to JSON."""

    def export(self, tasks: List[Task], filepath: str) -> None:
        data = [task.to_dict() for task in tasks]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


class CsvExporter:
    """Exports tasks to CSV."""

    def export(self, tasks: List[Task], filepath: str) -> None:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow([
                "id",
                "title",
                "description",
                "status",
                "priority",
                "assignee",
                "created_at"
            ])

            for task in tasks:
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.assignee,
                    task.created_at.isoformat()
                ])