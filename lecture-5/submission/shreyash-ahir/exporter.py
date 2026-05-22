"""
exporter.py - TaskExporter components.

Single Responsibility: serialise a list of Task objects to an external format.

Two concrete implementations of ITaskExporter are provided:
  - JsonExporter  — writes a JSON file (or returns JSON string).
  - CsvExporter   — writes a CSV file (or returns CSV string).

Both satisfy the ITaskExporter protocol.
"""

import csv
import io
import json
from datetime import datetime
from typing import List

from models import Task


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _task_to_flat_dict(task: Task) -> dict:
    """Convert a Task to a flat dict suitable for CSV/JSON export."""
    return {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "assignee_id": task.assignee_id or "",
        "due_date": task.due_date.isoformat() if task.due_date else "",
        "tags": ",".join(task.tags),
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# Implementation 1: JSON
# ---------------------------------------------------------------------------

class JsonExporter:
    """
    Exports tasks to JSON format.

    If *destination* is a file path (ends with .json), writes to disk and
    returns the path.  Otherwise returns the JSON string directly — handy
    for tests that don't want side-effects.
    """

    def export(self, tasks: List[Task], destination: str) -> str:
        rows = [_task_to_flat_dict(t) for t in tasks]
        json_str = json.dumps(rows, indent=2)

        if destination.endswith(".json"):
            with open(destination, "w", encoding="utf-8") as fh:
                fh.write(json_str)
            return destination

        return json_str


# ---------------------------------------------------------------------------
# Implementation 2: CSV
# ---------------------------------------------------------------------------

class CsvExporter:
    """
    Exports tasks to CSV format.

    Same write-or-return contract as JsonExporter.
    Demonstrates the ITaskExporter interface is satisfied by a completely
    different serialisation strategy without changing TaskManager.
    """

    COLUMNS = [
        "task_id", "title", "description", "status", "priority",
        "assignee_id", "due_date", "tags", "created_at", "updated_at",
    ]

    def export(self, tasks: List[Task], destination: str) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.COLUMNS)
        writer.writeheader()
        for task in tasks:
            writer.writerow(_task_to_flat_dict(task))

        csv_str = output.getvalue()

        if destination.endswith(".csv"):
            with open(destination, "w", encoding="utf-8", newline="") as fh:
                fh.write(csv_str)
            return destination

        return csv_str
