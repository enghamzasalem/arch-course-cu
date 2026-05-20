"""
Task Manager - Main Orchestrator

Coordinates components using dependency injection.
"""

from typing import List

from models import Task
from components.validator import TaskValidator
from components.repository import ITaskRepository
from components.search import TaskSearch
from components.exporter import ITaskExporter
from components.notifier import TaskNotifier


class TaskManager:
    """
    Main application service coordinating all components.
    """

    def __init__(
        self,
        repository: ITaskRepository,
        validator: TaskValidator,
        search: TaskSearch,
        exporter: ITaskExporter,
        notifier: TaskNotifier,
    ):
        """
        Dependencies are injected here.
        """
        self.repository = repository
        self.validator = validator
        self.search = search
        self.exporter = exporter
        self.notifier = notifier

    # -----------------------------
    # Task Operations
    # -----------------------------

    def create_task(self, task: Task) -> None:
        """Create and store a task."""
        self.validator.validate(task)
        self.repository.add(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks."""
        return self.repository.list()

    def delete_task(self, task_id: str) -> None:
        """Delete task by id."""
        self.repository.delete(task_id)

    # -----------------------------
    # Search
    # -----------------------------

    def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks by keyword."""
        tasks = self.repository.list()
        return self.search.search_by_keyword(tasks, keyword)

    # -----------------------------
    # Export
    # -----------------------------

    def export_tasks(self, filepath: str) -> None:
        """Export tasks using exporter implementation."""
        tasks = self.repository.list()
        self.exporter.export(tasks, filepath)

    # -----------------------------
    # Notifications
    # -----------------------------

    def send_reminders(self) -> None:
        """Send reminders for all tasks."""
        tasks = self.repository.list()

        for task in tasks:
            self.notifier.send_reminder(task)