"""
Demo script for Task Management System.
"""

from models import Task
from task_manager import TaskManager

from components.validator import TaskValidator
from components.repository import InMemoryTaskRepository
from components.search import TaskSearch
from components.exporter import JsonExporter
from components.notifier import TaskNotifier


def main():
    # -----------------------------
    # Create Components
    # -----------------------------

    repository = InMemoryTaskRepository()
    validator = TaskValidator()
    search = TaskSearch()
    exporter = JsonExporter()
    notifier = TaskNotifier()

    # -----------------------------
    # Inject dependencies
    # -----------------------------

    manager = TaskManager(
        repository=repository,
        validator=validator,
        search=search,
        exporter=exporter,
        notifier=notifier,
    )

    # -----------------------------
    # Create Tasks
    # -----------------------------

    task1 = Task(id="1", title="Finish assignment", assignee="Alice")
    task2 = Task(id="2", title="Review PR", assignee="Bob")

    manager.create_task(task1)
    manager.create_task(task2)

    # -----------------------------
    # List Tasks
    # -----------------------------

    print("All Tasks:")
    for task in manager.get_tasks():
        print(task)

    # -----------------------------
    # Search
    # -----------------------------

    print("\nSearch 'finish':")
    results = manager.search_tasks("finish")

    for task in results:
        print(task)

    # -----------------------------
    # Export
    # -----------------------------

    manager.export_tasks("tasks.json")

    # -----------------------------
    # Reminders
    # -----------------------------

    manager.send_reminders()


if __name__ == "__main__":
    main()