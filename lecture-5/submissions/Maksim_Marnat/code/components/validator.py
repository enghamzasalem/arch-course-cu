from typing import Optional, Tuple
from ..models import TaskPriority, TaskStatus

class TaskValidator:
    def validate_new_task(self, title: str, description: str = "", assignee: Optional[str] = None, priority: TaskPriority = TaskPriority.MEDIUM) -> Tuple[bool, Optional[str]]:
        if not title or not title.strip():
            return False, "Title must not be empty"
        return True, None

    def validate_status_transition(self, current: TaskStatus, new_status: TaskStatus) -> Tuple[bool, Optional[str]]:
        if current == TaskStatus.DONE and new_status != TaskStatus.DONE:
            return False, "Cannot move from DONE"
        return True, None
