from typing import List, Optional
from models import Task


class TaskSearch:
    # Search in title/description and also filter by some fields

    def search(self, tasks: List[Task], keyword: str):
        keyword = keyword.lower()
        result = []

        for t in tasks:
            if keyword in t.title.lower() or keyword in t.description.lower():
                result.append(t)

        return result

    def filter_tasks(
        self,
        tasks: List[Task],
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ):
        result = tasks

        if assignee is not None:
            result = [t for t in result if t.assignee == assignee]

        if status is not None:
            result = [t for t in result if t.status.value == status]

        if priority is not None:
            result = [t for t in result if t.priority.value == priority]

        return result