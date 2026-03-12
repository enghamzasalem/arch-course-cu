from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Task:
    task_id: int
    title: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "Pending"

    def to_dict(self) -> dict:
        return asdict(self)
