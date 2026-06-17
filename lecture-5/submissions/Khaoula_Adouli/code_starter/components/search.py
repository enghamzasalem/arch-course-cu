"""

Task Search Component
 
Responsible for filtering and searching tasks.

"""
 
from typing import List

from models import Task
 
 
class TaskSearch:

    """Search and filter tasks."""
 
    def by_status(self, tasks: List[Task], status) -> List[Task]:

        return [t for t in tasks if t.status == status]
 
    def by_assignee(self, tasks: List[Task], assignee: str) -> List[Task]:

        return [t for t in tasks if t.assignee == assignee]
 