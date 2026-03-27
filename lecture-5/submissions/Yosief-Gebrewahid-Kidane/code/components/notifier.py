"""
Task Notifier Component
Simulates sending task reminders.
"""

from models import Task


class TaskNotifier:
    """Sends task notifications."""

    def send_reminder(self, task: Task) -> None:
        """Simulate reminder notification."""

        if task.assignee:
            print(f"[Reminder] Task '{task.title}' assigned to {task.assignee}")
        else:
            print(f"[Reminder] Task '{task.title}' has no assignee")