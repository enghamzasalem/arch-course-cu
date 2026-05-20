"""
Task Search Component
Handles filtering and searching tasks.
"""

from typing import List
from models import Task, TaskStatus


class TaskSearch:
    """Provides search capabilities."""

    def filter_by_status(self, tasks: List[Task], status: TaskStatus) -> List[Task]:
        """Return tasks matching status."""
        return [task for task in tasks if task.status == status]

    def search_by_keyword(self, tasks: List[Task], keyword: str) -> List[Task]:
        """Search tasks by keyword."""

        if not keyword:
            return []

        keyword = keyword.lower()

        return [
            task for task in tasks
            if keyword in task.title.lower()
            or keyword in task.description.lower()
        ]