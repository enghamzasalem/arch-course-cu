class TaskNotifier:

    def send_reminder(self, task):
        print(f"Reminder: Task '{task.title}' assigned to {task.assigned_to}")