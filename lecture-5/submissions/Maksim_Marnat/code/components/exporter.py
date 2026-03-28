import csv
import json
from pathlib import Path
from typing import Iterable
from ..models import Task
from .interfaces import ITaskExporter

class JsonTaskExporter(ITaskExporter):
    def export(self, tasks: Iterable[Task], destination: str) -> None:
        Path(destination).write_text(json.dumps([t.to_dict() for t in tasks], indent=2), encoding="utf-8")

class CsvTaskExporter(ITaskExporter):
    def export(self, tasks: Iterable[Task], destination: str) -> None:
        rows = [t.to_dict() for t in tasks]
        path = Path(destination)
        headers = ["id", "title", "description", "status", "priority", "assignee", "created_at"]
        if rows:
            headers = list(rows[0].keys())
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)
