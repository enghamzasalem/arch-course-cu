"""
search.py - TaskSearch component.

Single Responsibility: filter a list of tasks by various criteria.

This component has no knowledge of how tasks are stored or exported.
It receives a plain list and returns a filtered plain list.
All filter logic lives here — the "one reason to change" is
"the rules for how tasks are searched or filtered changed".
"""

from typing import List, Optional
from models import Task, TaskStatus, TaskPriority


class TaskSearch:
    """
    Stateless search/filter engine for Task objects.

    All methods accept a task list and return a new list.
    No side effects; easy to unit-test without any mock objects.
    """

    def by_status(self, tasks: List[Task], status: TaskStatus) -> List[Task]:
        """Return tasks whose status matches *status*."""
        return [t for t in tasks if t.status == status]

    def by_priority(self, tasks: List[Task], priority: TaskPriority) -> List[Task]:
        """Return tasks whose priority matches *priority*."""
        return [t for t in tasks if t.priority == priority]

    def by_assignee(self, tasks: List[Task], user_id: str) -> List[Task]:
        """Return tasks assigned to *user_id*."""
        return [t for t in tasks if t.assignee_id == user_id]

    def by_keyword(self, tasks: List[Task], keyword: str) -> List[Task]:
        """
        Case-insensitive substring search on title and description.
        Keeps it simple — no external search library required.
        """
        kw = keyword.lower()
        return [
            t for t in tasks
            if kw in t.title.lower() or kw in t.description.lower()
        ]

    def by_tag(self, tasks: List[Task], tag: str) -> List[Task]:
        """Return tasks that include *tag* in their tags list."""
        return [t for t in tasks if tag in t.tags]

    def overdue(self, tasks: List[Task]) -> List[Task]:
        """Return tasks that are past their due date and not yet done."""
        from datetime import datetime
        now = datetime.utcnow()
        return [
            t for t in tasks
            if t.due_date and t.due_date < now and t.status != TaskStatus.DONE
        ]
