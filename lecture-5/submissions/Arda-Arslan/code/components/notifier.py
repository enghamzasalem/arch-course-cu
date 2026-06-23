from models import Task


class TaskNotifier:
    # Prints a reminder message

    def remind(self, task: Task):
        user = task.assignee if task.assignee else "someone"
        print(f"Reminder for task '{task.title}' -> {user}")