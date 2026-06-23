from typing import List
from models import Task, TaskStatus


class TaskSearch:

    def by_assignee(self, tasks: List[Task], assignee: str) -> List[Task]:
        return [t for t in tasks if t.assignee == assignee]

    def by_status(self, tasks: List[Task], status: TaskStatus) -> List[Task]:
        return [t for t in tasks if t.status == status]

    def by_keyword(self, tasks: List[Task], keyword: str) -> List[Task]:
        keyword = keyword.lower()
        return [t for t in tasks if keyword in t.title.lower()]