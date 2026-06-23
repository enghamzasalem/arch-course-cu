"""
Task Exporter Component

Responsible for exporting tasks to different formats.
"""

from abc import ABC, abstractmethod
from typing import List
import json
import csv

from models import Task


# ================================
# Interface
# ================================

class ITaskExporter(ABC):
    """Interface for exporting tasks."""

    @abstractmethod
    def export(self, tasks: List[Task], file_path: str) -> None:
        pass


# ================================
# JSON Exporter
# ================================

class JsonExporter(ITaskExporter):
    """Exports tasks to JSON file."""

    def export(self, tasks: List[Task], file_path: str) -> None:
        data = [task.to_dict() for task in tasks]

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)


# ================================
# CSV Exporter
# ================================

class CsvExporter(ITaskExporter):
    """Exports tasks to CSV file."""

    def export(self, tasks: List[Task], file_path: str) -> None:
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(["id", "title", "description", "status", "priority", "assignee"])

            for task in tasks:
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.assignee
                ])