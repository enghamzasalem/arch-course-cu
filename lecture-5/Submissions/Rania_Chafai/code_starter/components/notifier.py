"""
Task Notifier Component

Responsible for sending task reminders.
"""

from models import Task


class TaskNotifier:
    """Sends reminders for tasks."""

    def send_reminder(self, task: Task) -> None:
        print(f"Reminder: Task '{task.title}' assigned to {task.assignee}")