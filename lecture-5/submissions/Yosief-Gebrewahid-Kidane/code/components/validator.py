"""
Task Validator Component
Responsible only for validating task data.
"""

from typing import Optional
from models import Task


class TaskValidator:
    """Validates Task objects."""

    def validate(self, task: Task) -> bool:
        """Validate a task object."""

        if not task.id:
            raise ValueError("Task ID cannot be empty")

        if not task.title:
            raise ValueError("Task title cannot be empty")

        self.validate_assignee(task.assignee)

        return True

    def validate_assignee(self, assignee: Optional[str]) -> bool:
        """Validate assignee value."""

        if assignee is None:
            return True

        if len(assignee) < 2:
            raise ValueError("Assignee name too short")

        return True

