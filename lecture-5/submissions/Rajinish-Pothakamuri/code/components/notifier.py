"""
Task Management System - Notifier Component
"""

from typing import Protocol

from models import Task


class ITaskNotifier(Protocol):
    """Interface for task reminders."""

    def send_reminder(self, task: Task, message: str) -> None: ...


class ConsoleTaskNotifier:
    """Print reminders to the console."""

    def send_reminder(self, task: Task, message: str) -> None:
        print(f"[Reminder] Task {task.id} ({task.title}): {message}")


class SilentTaskNotifier:
    """No-op notifier for testing or disabling notifications."""

    def send_reminder(self, task: Task, message: str) -> None:
        return None
