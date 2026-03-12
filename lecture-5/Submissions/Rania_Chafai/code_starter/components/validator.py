"""
Task Validator Component

Responsible for validating task data.
"""

from models import Task


class TaskValidator:
    """Validates task data."""

    def validate(self, task: Task) -> None:
        if not task.title:
            raise ValueError("Task title cannot be empty")

        if len(task.title) < 3:
            raise ValueError("Task title must have at least 3 characters")