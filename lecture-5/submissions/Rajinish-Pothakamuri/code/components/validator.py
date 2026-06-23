"""
Task Management System - Validator Component
"""

from typing import List, Tuple, Protocol

from models import Task

class ITaskValidator(Protocol):
    def validate_new(self, task: Task) -> Tuple[bool, List[str]]: ...
    def validate_update(self, task: Task) -> Tuple[bool, List[str]]: ...
    
class TaskValidator:
    """
    Single Responsibility: validate task data and business rules.
    One reason to change: validation rules change.
    """

    def validate_new(self, task: Task) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not task.id or not task.id.strip():
            errors.append("Task id is required")
        if not task.title or not task.title.strip():
            errors.append("Task title is required")
        if len(task.title.strip()) < 3:
            errors.append("Task title must be at least 3 characters")

        return len(errors) == 0, errors

    def validate_update(self, task: Task) -> Tuple[bool, List[str]]:
        """Reuse same rules for updates in this assignment."""
        return self.validate_new(task)
