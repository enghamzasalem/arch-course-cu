"""
Task Management System - Orchestrator
"""

from typing import Dict, List, Optional

from models import Task, TaskStatus, TaskPriority
from components.validator import ITaskValidator
from components.repository import ITaskRepository
from components.search import TaskSearch
from components.exporter import ITaskExporter
from components.notifier import ITaskNotifier


class TaskManager:
    """
    Orchestrates task operations.
    Single Responsibility: coordinate components and workflow.
    """

    def __init__(
        self,
        validator: ITaskValidator,
        repository: ITaskRepository,
        search: TaskSearch,
        exporters: Dict[str, ITaskExporter],
        notifier: ITaskNotifier,
    ) -> None:
        self._validator = validator
        self._repository = repository
        self._search = search
        self._exporters = exporters
        self._notifier = notifier

    def create_task(
        self,
        task_id: str,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
        )
        valid, errors = self._validator.validate_new(task)
        if not valid:
            raise ValueError(", ".join(errors))
        self._repository.add(task)
        return task

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> Task:
        task = self._repository.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority

        valid, errors = self._validator.validate_update(task)
        if not valid:
            raise ValueError(", ".join(errors))

        self._repository.update(task)
        return task

    def delete_task(self, task_id: str) -> None:
        self._repository.delete(task_id)

    def assign_task(self, task_id: str, assignee: str) -> Task:
        task = self._repository.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")
        task.assignee = assignee
        self._repository.update(task)
        return task

    def list_tasks(self) -> List[Task]:
        return self._repository.list_all()

    def search_tasks(self, text: str) -> List[Task]:
        return self._search.search_text(text)

    def filter_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return self._search.filter_by_status(status)

    def filter_tasks_by_assignee(self, assignee: Optional[str]) -> List[Task]:
        return self._search.filter_by_assignee(assignee)

    def export_tasks(self, format_name: str) -> str:
        tasks = self._repository.list_all()
        exporter = self._exporters.get(format_name.lower())
        if not exporter:
            raise KeyError(f"Exporter '{format_name}' not configured")
        return exporter.export(tasks)

    def send_task_reminder(self, task_id: str, message: str) -> None:
        task = self._repository.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")
        self._notifier.send_reminder(task, message)
