from models import Task

class TaskNotifier:
    """Component for sending task notifications."""
    
    def send_reminder(self, task: Task) -> None:
        """Send a reminder for a task."""
        print(f"[TaskNotifier] Executing: send_reminder for task '{task.title}'")
