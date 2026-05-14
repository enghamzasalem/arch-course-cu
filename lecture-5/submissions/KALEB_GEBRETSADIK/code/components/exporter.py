from typing import List
from models import Task
from interfaces import ITaskExporter

class JsonExporter:
    """JSON implementation of task exporter."""
    
    def export(self, tasks: List[Task], format: str = "json") -> str:
        """Export tasks to JSON format."""
        print(f"[JsonExporter] Executing: export {len(tasks)} tasks to JSON format")
        return ""

class CsvExporter:
    """CSV implementation of task exporter."""
    
    def export(self, tasks: List[Task], format: str = "csv") -> str:
        """Export tasks to CSV format."""
        print(f"[CsvExporter] Executing: export {len(tasks)} tasks to CSV format")
        return ""
