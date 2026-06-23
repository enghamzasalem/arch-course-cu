from models import Task


class TaskNotifier:

    def send_reminder(self, task: Task):

        if task.assignee:
            print(f"Reminder: {task.assignee} -> '{task.title}'")