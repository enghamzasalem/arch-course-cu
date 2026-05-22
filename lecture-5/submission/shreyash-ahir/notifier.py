"""
notifier.py - TaskNotifier component.

Single Responsibility: decide when and how to notify users about tasks.
In this simulation, all output goes to the console.  In production you
would swap the print() calls for email/SMS/Slack API calls — without
touching any other component.

The "one reason to change" for this component:
  the notification channel or the trigger rules changed.
"""

from datetime import datetime, timedelta
from typing import List

from models import Task, TaskStatus


class TaskNotifier:
    """
    Sends reminders for tasks that are due soon or overdue.

    All notification logic lives here.  Other components never decide
    whether a notification should be sent.
    """

    def __init__(self, warning_hours: int = 24) -> None:
        """
        Args:
            warning_hours: How many hours before due_date to start warning.
        """
        self._warning_hours = warning_hours

    def send_reminders(self, tasks: List[Task]) -> List[str]:
        """
        Evaluate *tasks* and emit a console reminder for each task that
        is due within *warning_hours* or already overdue.

        Returns a list of the messages sent (useful for logging/testing).
        """
        messages = []
        now = datetime.utcnow()
        threshold = now + timedelta(hours=self._warning_hours)

        for task in tasks:
            if task.status == TaskStatus.DONE:
                continue
            if task.due_date is None:
                continue

            if task.due_date < now:
                msg = self._format_overdue(task)
            elif task.due_date <= threshold:
                msg = self._format_due_soon(task, task.due_date - now)
            else:
                continue

            print(msg)
            messages.append(msg)

        return messages

    def notify_assignment(self, task: Task, user_name: str) -> str:
        """Notify a user that they have been assigned a task."""
        msg = (
            f"[ASSIGNMENT] '{task.title}' (id={task.task_id}) "
            f"has been assigned to {user_name}."
        )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Private formatting helpers
    # ------------------------------------------------------------------

    def _format_overdue(self, task: Task) -> str:
        return (
            f"[OVERDUE] Task '{task.title}' (id={task.task_id}) "
            f"was due on {task.due_date.strftime('%Y-%m-%d %H:%M')} UTC."
        )

    def _format_due_soon(self, task: Task, remaining: timedelta) -> str:
        hours = int(remaining.total_seconds() // 3600)
        return (
            f"[REMINDER] Task '{task.title}' (id={task.task_id}) "
            f"is due in ~{hours} hour(s)."
        )
