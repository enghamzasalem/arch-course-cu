from typing import List, Optional
from models import Task
from interfaces import ITaskStorage

class InMemoryTaskRepository:
    """In-memory implementation of task storage."""
    
    def add(self, task: Task) -> None:
        """Add a task to the repository."""
        print(f"[InMemoryTaskRepository] Executing: add task '{task.id}'")
        
    def get_all(self) -> List[Task]:
        """Retrieve all tasks."""
        print("[InMemoryTaskRepository] Executing: get_all tasks")
        return []
        
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by its ID."""
        print(f"[InMemoryTaskRepository] Executing: find_by_id '{task_id}'")
        return None

class FileTaskRepository:
    """File-based implementation of task storage."""
    
    def add(self, task: Task) -> None:
        """Add a task to the file storage."""
        print(f"[FileTaskRepository] Executing: add task '{task.id}' to file")
        
    def get_all(self) -> List[Task]:
        """Retrieve all tasks from file."""
        print("[FileTaskRepository] Executing: get_all tasks from file")
        return []
        
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by its ID in file."""
        print(f"[FileTaskRepository] Executing: find_by_id '{task_id}' in file")
        return None
