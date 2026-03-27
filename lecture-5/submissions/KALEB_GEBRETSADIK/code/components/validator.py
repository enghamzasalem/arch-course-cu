from models import Task

class TaskValidator:
    """Component for validating task data."""
    
    def validate(self, task: Task) -> bool:
        """Validate a task."""
        print(f"[TaskValidator] Executing: validate task '{task.title}'")
        return True
