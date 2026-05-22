"""
validator.py - TaskValidator component.

Single Responsibility: decide whether task data is valid before it is
stored.  Raises ValueError with a clear message when validation fails.
No I/O, no storage, no formatting — just rules.
"""

from datetime import datetime
from models import Task


class TaskValidator:
    """
    Validates the fields of a Task object.

    All rules live here.  If the business decides "title must be at least
    5 characters", this is the only file that changes.
    """

    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 120

    def validate(self, task: Task) -> None:
        """
        Validate *task*.  Raises ValueError if any rule is broken.
        Callers should catch ValueError and surface it to the user.
        """
        self._check_title(task.title)
        self._check_due_date(task.due_date)

    # ------------------------------------------------------------------
    # Private helpers — each rule is its own method so they can be
    # tested independently and extended without editing the others.
    # ------------------------------------------------------------------

    def _check_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ValueError("Task title must not be empty.")
        length = len(title.strip())
        if length < self.MIN_TITLE_LENGTH:
            raise ValueError(
                f"Task title must be at least {self.MIN_TITLE_LENGTH} characters "
                f"(got {length})."
            )
        if length > self.MAX_TITLE_LENGTH:
            raise ValueError(
                f"Task title must be at most {self.MAX_TITLE_LENGTH} characters "
                f"(got {length})."
            )

    def _check_due_date(self, due_date) -> None:
        if due_date is not None and due_date < datetime.utcnow():
            raise ValueError(
                f"Due date {due_date.isoformat()} is in the past."
            )
