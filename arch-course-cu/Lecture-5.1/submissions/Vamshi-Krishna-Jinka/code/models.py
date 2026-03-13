from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str
    assigned_to: str
    status: str = "pending"