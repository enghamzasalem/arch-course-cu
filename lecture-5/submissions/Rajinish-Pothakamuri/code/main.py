"""
Task Management System - Demo Usage
"""

from pathlib import Path

from models import TaskPriority, TaskStatus
from components.validator import TaskValidator
from components.repository import InMemoryTaskRepository, FileTaskRepository
from components.search import TaskSearch
from components.exporter import JsonTaskExporter, CsvTaskExporter
from components.notifier import ConsoleTaskNotifier, SilentTaskNotifier
from task_manager import TaskManager


def build_manager_with_inmemory() -> TaskManager:
    repo = InMemoryTaskRepository()
    search = TaskSearch(repo)
    return TaskManager(
        validator=TaskValidator(),
        repository=repo,
        search=search,
        exporters={
            "json": JsonTaskExporter(),
            "csv": CsvTaskExporter(),
        },
        notifier=ConsoleTaskNotifier(),
    )


def build_manager_with_file(file_path: str) -> TaskManager:
    repo = FileTaskRepository(file_path)
    search = TaskSearch(repo)
    return TaskManager(
        validator=TaskValidator(),
        repository=repo,
        search=search,
        exporters={
            "json": JsonTaskExporter(),
            "csv": CsvTaskExporter(),
        },
        notifier=SilentTaskNotifier(),
    )


def run_demo() -> None:
    print("=== Task Manager Demo (In-Memory Repository) ===")
    manager = build_manager_with_inmemory()

    manager.create_task("T-001", "Design component diagram", priority=TaskPriority.HIGH)
    manager.create_task("T-002", "Write cohesion analysis", description="Part 2 doc")
    manager.assign_task("T-001", "Alicia")
    manager.update_task("T-002", status=TaskStatus.IN_PROGRESS)

    print("All tasks:")
    for task in manager.list_tasks():
        print("-", task.to_dict())

    print("Search 'diagram':", [t.id for t in manager.search_tasks("diagram")])
    print("Filter status IN_PROGRESS:", [t.id for t in manager.filter_tasks_by_status(TaskStatus.IN_PROGRESS)])

    print("Export JSON:")
    print(manager.export_tasks("json"))

    manager.send_task_reminder("T-001", "Due tomorrow at 9am")

    print("\n=== Task Manager Demo (File Repository) ===")
    data_path = str(Path(__file__).parent / "data" / "tasks.json")
    file_manager = build_manager_with_file(data_path)
    file_manager.create_task("T-100", "Write README", description="Submission instructions")
    print("Export CSV:")
    print(file_manager.export_tasks("csv"))


if __name__ == "__main__":
    run_demo()
