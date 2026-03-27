from typing import Dict, Tuple, Optional
from models import TaskStatus, TaskPriority


class TaskValidator:
    # Checks task input before saving or updating

    def validate_new_task(self, data: Dict) -> Tuple[bool, Optional[str]]:
        if not data.get("id"):
            return False, "Task id missing"

        if not data.get("title"):
            return False, "Task title missing"

        if len(data["title"].strip()) < 3:
            return False, "Title too short"

        return True, None

    def validate_update(self, data: Dict) -> Tuple[bool, Optional[str]]:
        if "title" in data:
            if len(data["title"].strip()) < 3:
                return False, "Title too short"

        if "status" in data:
            valid = [s.value for s in TaskStatus]
            if data["status"] not in valid:
                return False, "Invalid status"

        if "priority" in data:
            valid = [p.value for p in TaskPriority]
            if data["priority"] not in valid:
                return False, "Invalid priority"

        return True, None