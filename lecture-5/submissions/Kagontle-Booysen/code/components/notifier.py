class TaskNotifier:
    def send_reminder(self, task):
        if task.assigned_to:
            print(f"Reminder: Task '{task.title}' is assigned to {task.assigned_to} and is currently '{task.status}'.")
        else:
            print(f"Reminder: Task '{task.title}' is not yet assigned to any user.")
