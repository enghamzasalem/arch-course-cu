"""
Task Management System - Search/Filter Component
"""

from typing import List, Optional

from models import Task, TaskStatus
from components.repository import ITaskRepository


class TaskSearch:
    """
    Single Responsibility: filtering and searching tasks.
    One reason to change: search/filter rules change.
    """

    def __init__(self, repository: ITaskRepository) -> None:
        self._repository = repository

    def search_text(self, text: str) -> List[Task]:
        text = text.lower().strip()
        if not text:
            return []
        return [
            t for t in self._repository.list_all()
            if text in t.title.lower() or text in t.description.lower()
        ]

    def filter_by_status(self, status: TaskStatus) -> List[Task]:
        return [t for t in self._repository.list_all() if t.status == status]

    def filter_by_assignee(self, assignee: Optional[str]) -> List[Task]:
        if assignee is None:
            return [t for t in self._repository.list_all() if t.assignee is None]
        assignee = assignee.lower().strip()
        return [
            t for t in self._repository.list_all()
            if (t.assignee or "").lower() == assignee
        ]
