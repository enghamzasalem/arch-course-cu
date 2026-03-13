from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ItemStatus(Enum):
    """Task status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class ItemPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskItem:
    """Task entity."""
    item_id: str
    title: str
    description: str = ""
    status: ItemStatus = ItemStatus.PENDING
    priority: ItemPriority = ItemPriority.MEDIUM
    owner: Optional[str] = None
    deadline: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """Convert to dictionary for saving."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "owner": self.owner,
            "deadline": self.deadline,
            "labels": self.labels,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary."""
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            description=data.get("description", ""),
            status=ItemStatus(data.get("status", "pending")),
            priority=ItemPriority(data.get("priority", 2)),
            owner=data.get("owner"),
            deadline=data.get("deadline"),
            labels=data.get("labels", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )