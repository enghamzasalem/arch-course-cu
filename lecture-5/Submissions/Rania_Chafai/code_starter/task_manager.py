"""
Task Manager

Main orchestrator that coordinates all components.
"""

from typing import List
from models import Task
from components.repository import ITaskRepository
from components.validator import TaskValidator
from components.search import TaskSearch
from components.exporter import ITaskExporter
from components.notifier import TaskNotifier


class TaskManager:
    """Main application service."""

    def __init__(
        self,
        repository: ITaskRepository,
        validator: TaskValidator,
        search: TaskSearch,
        exporter: ITaskExporter,
        notifier: TaskNotifier
    ):
        self.repository = repository
        self.validator = validator
        self.search = search
        self.exporter = exporter
        self.notifier = notifier

    # ================================
    # Task CRUD
    # ================================

    def create_task(self, task: Task) -> None:
        self.validator.validate(task)
        self.repository.add(task)

    def update_task(self, task: Task) -> None:
        self.validator.validate(task)
        self.repository.update(task)

    def delete_task(self, task_id: str) -> None:
        self.repository.delete(task_id)

    def list_tasks(self) -> List[Task]:
        return self.repository.get_all()

    # ================================
    # Search
    # ================================

    def search_by_status(self, status):
        tasks = self.repository.get_all()
        return self.search.by_status(tasks, status)

    def search_by_assignee(self, assignee: str):
        tasks = self.repository.get_all()
        return self.search.by_assignee(tasks, assignee)

    # ================================
    # Export
    # ================================

    def export_tasks(self, file_path: str) -> None:
        tasks = self.repository.get_all()
        self.exporter.export(tasks, file_path)

    # ================================
    # Notifications
    # ================================

    def send_reminder(self, task_id: str) -> None:
        task = self.repository.get_by_id(task_id)
        if task:
            self.notifier.send_reminder(task)