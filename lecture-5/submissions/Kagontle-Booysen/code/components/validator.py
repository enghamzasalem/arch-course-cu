class TaskValidator:
    ALLOWED_STATUSES = {"Pending", "In Progress", "Completed"}

    def validate_task_data(self, task_id, title, description, assigned_to=None, status="Pending"):
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("task_id must be a positive integer.")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")

        if not isinstance(description, str) or not description.strip():
            raise ValueError("description must be a non-empty string.")

        if assigned_to is not None and (not isinstance(assigned_to, str) or not assigned_to.strip()):
            raise ValueError("assigned_to must be a non-empty string or None.")

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {self.ALLOWED_STATUSES}.")
