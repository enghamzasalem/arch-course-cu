class TaskValidator:

    def validate(self, task):
        if not task.title:
            raise ValueError("Task title cannot be empty")

        if not task.assigned_to:
            raise ValueError("Task must be assigned to someone")

        return True