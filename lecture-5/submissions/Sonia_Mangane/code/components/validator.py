from models import Task


class TaskValidator:
    """Validates task data."""

    def validate(self, task: Task):

        if not task.id:
            raise ValueError("Task ID is required")

        if not task.title:
            raise ValueError("Task title cannot be empty")

        if len(task.title) < 3:
            raise ValueError("Title must be at least 3 characters")

        return True