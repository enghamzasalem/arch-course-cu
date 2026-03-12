from pathlib import Path
from .components.exporter import CsvTaskExporter, JsonTaskExporter
from .components.repository import FileTaskRepository, InMemoryTaskRepository
from .models import TaskPriority, TaskStatus
from .task_manager import TaskManager

def demo() -> None:
    # Config 1: in-memory + JSON
    m1 = TaskManager(storage=InMemoryTaskRepository(), exporter=JsonTaskExporter())
    m1.create_task("T-1", "Report", assignee="alice", priority=TaskPriority.HIGH)
    m1.create_task("T-2", "Refactor", assignee="bob", priority=TaskPriority.MEDIUM)
    m1.update_status("T-1", TaskStatus.DONE)
    m1.export_tasks(m1.list_tasks(), "tasks.json")
    m1.send_reminders_for_assignee("bob")
    # Config 2: file + CSV (swap without changing TaskManager)
    m2 = TaskManager(storage=FileTaskRepository(Path(".") / "tasks.json"), exporter=CsvTaskExporter())
    m2.create_task("T-10", "Extra task", assignee="alice")
    m2.export_tasks(m2.list_tasks(), "tasks.csv")
    print("Done: tasks.json, tasks.csv")

if __name__ == "__main__":
    demo()
