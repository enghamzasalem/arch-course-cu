"""
Demo application
"""

from models import Task, TaskStatus, TaskPriority
from components.repository import InMemoryTaskRepository
from components.validator import TaskValidator
from components.search import TaskSearch
from components.exporter import JsonExporter
from components.notifier import TaskNotifier
from task_manager import TaskManager


def main():
    repository = InMemoryTaskRepository()
    validator = TaskValidator()
    search = TaskSearch()
    exporter = JsonExporter()
    notifier = TaskNotifier()

    manager = TaskManager(
        repository,
        validator,
        search,
        exporter,
        notifier
    )

    # Create task
    task = Task(
        id="1",
        title="Finish architecture assignment",
        description="Complete modular design assignment",
        priority=TaskPriority.HIGH,
        assignee="Rania"
    )

    manager.create_task(task)

    # List tasks
    tasks = manager.list_tasks()
    print("Tasks:", tasks)

    # Export tasks
    manager.export_tasks("tasks.json")

    # Send reminder
    manager.send_reminder("1")


if __name__ == "__main__":
    main()