"""
task_manager.py - TaskManager orchestrator.

TaskManager is the single entry-point for all use-cases in the system.
It does NOT implement any business logic itself — it delegates to the
injected components.

Dependency Injection via constructor:
  All dependencies are received as constructor arguments typed as
  interfaces (ITaskStorage, ITaskExporter), never as concrete classes.
  Swapping InMemoryTaskRepository for FileTaskRepository, or JsonExporter
  for CsvExporter, requires zero changes here.

Single Responsibility of TaskManager:
  Coordinate the workflow between components for each use-case.
  Its "one reason to change" is: the high-level workflow between
  components changed (e.g., a new validation step is added to the
  create-task workflow).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from interfaces import ITaskStorage, ITaskExporter
from models import Task, TaskStatus, TaskPriority, User
from components.validator import TaskValidator
from components.search import TaskSearch
from components.notifier import TaskNotifier


class TaskManager:
    """
    Coordinates all task-management use-cases.

    Constructor arguments (all injected; no concrete classes imported):
      storage   — anything satisfying ITaskStorage
      exporter  — anything satisfying ITaskExporter
      validator — TaskValidator (no interface needed; it has no variants)
      searcher  — TaskSearch    (same reasoning)
      notifier  — TaskNotifier  (same reasoning)
    """

    def __init__(
        self,
        storage: ITaskStorage,
        exporter: ITaskExporter,
        validator: Optional[TaskValidator] = None,
        searcher: Optional[TaskSearch] = None,
        notifier: Optional[TaskNotifier] = None,
    ) -> None:
        self._storage = storage
        self._exporter = exporter
        self._validator = validator or TaskValidator()
        self._searcher = searcher or TaskSearch()
        self._notifier = notifier or TaskNotifier()
        self._users: dict = {}   # user_id -> User (simple in-memory user store)

    # ------------------------------------------------------------------
    # User management (minimal, supports assignment demo)
    # ------------------------------------------------------------------

    def add_user(self, name: str, email: str) -> User:
        user = User(user_id=str(uuid.uuid4()), name=name, email=email)
        self._users[user.user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    # ------------------------------------------------------------------
    # Task CRUD
    # ------------------------------------------------------------------

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Task:
        task = Task(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags or [],
        )
        self._validator.validate(task)   # raises ValueError on invalid data
        self._storage.save(task)
        return task

    def update_task(self, task_id: str, **fields) -> Task:
        task = self._get_or_raise(task_id)
        for key, value in fields.items():
            if not hasattr(task, key):
                raise ValueError(f"Task has no field '{key}'.")
            setattr(task, key, value)
        self._validator.validate(task)
        self._storage.save(task)
        return task

    def delete_task(self, task_id: str) -> bool:
        return self._storage.delete(task_id)

    def get_task(self, task_id: str) -> Task:
        return self._get_or_raise(task_id)

    def list_tasks(self) -> List[Task]:
        return self._storage.list_all()

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    def assign_task(self, task_id: str, user_id: str) -> Task:
        if user_id not in self._users:
            raise ValueError(f"No user with id '{user_id}'.")
        task = self._get_or_raise(task_id)
        task.assignee_id = user_id
        self._storage.save(task)
        user = self._users[user_id]
        self._notifier.notify_assignment(task, user.name)
        return task

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, keyword: str) -> List[Task]:
        return self._searcher.by_keyword(self.list_tasks(), keyword)

    def filter_by_status(self, status: TaskStatus) -> List[Task]:
        return self._searcher.by_status(self.list_tasks(), status)

    def filter_by_priority(self, priority: TaskPriority) -> List[Task]:
        return self._searcher.by_priority(self.list_tasks(), priority)

    def overdue_tasks(self) -> List[Task]:
        return self._searcher.overdue(self.list_tasks())

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_tasks(self, destination: str) -> str:
        return self._exporter.export(self.list_tasks(), destination)

    # ------------------------------------------------------------------
    # Reminders
    # ------------------------------------------------------------------

    def send_reminders(self) -> List[str]:
        return self._notifier.send_reminders(self.list_tasks())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_raise(self, task_id: str) -> Task:
        task = self._storage.get(task_id)
        if task is None:
            raise ValueError(f"Task '{task_id}' not found.")
        return task
