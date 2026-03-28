from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "description": self.description,
                "status": self.status.value, "priority": self.priority.value,
                "assignee": self.assignee, "created_at": self.created_at.isoformat()}

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(id=data["id"], title=data["title"], description=data.get("description", ""),
                   status=TaskStatus(data.get("status", "todo")), priority=TaskPriority(data.get("priority", "medium")),
                   assignee=data.get("assignee"),
                   created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now())
