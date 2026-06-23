"""
Task Management System - Exporter Component
"""

from typing import List, Protocol
import json
import csv
import io

from models import Task


class ITaskExporter(Protocol):
    """Interface for exporting tasks."""

    def export(self, tasks: List[Task]) -> str: ...


class JsonTaskExporter:
    """Export tasks to JSON string."""

    def export(self, tasks: List[Task]) -> str:
        return json.dumps([t.to_dict() for t in tasks], indent=2)


class CsvTaskExporter:
    """Export tasks to CSV string."""

    def export(self, tasks: List[Task]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "title",
                "description",
                "status",
                "priority",
                "assignee",
                "created_at",
            ],
        )
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.to_dict())
        return output.getvalue()
