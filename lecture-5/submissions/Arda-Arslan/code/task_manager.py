from typing import Dict, Optional
from models import Task, TaskStatus, TaskPriority

from components.repository import ITaskRepository
from components.validator import TaskValidator
from components.search import TaskSearch
from components.exporter import ITaskExporter
from components.notifier import TaskNotifier


class TaskManager:
    # Main class that connects the other parts

    def __init__(self, repo: ITaskRepository,
                 validator: TaskValidator,
                 search: TaskSearch,
                 exporter: ITaskExporter,
                 notifier: TaskNotifier):

        self.repo = repo
        self.validator = validator
        self.search = search
        self.exporter = exporter
        self.notifier = notifier

    def create(self, data: Dict):
        ok, err = self.validator.validate_new_task(data)

        if not ok:
            return err

        if self.repo.get(data["id"]):
            return "Task already exists"

        task = Task(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "todo")),
            priority=TaskPriority(data.get("priority", "medium")),
            assignee=data.get("assignee"),
        )

        self.repo.add(task)
        return "Task created"

    def update(self, task_id, updates):
        task = self.repo.get(task_id)

        if not task:
            return "Task not found"

        ok, err = self.validator.validate_update(updates)

        if not ok:
            return err

        if "title" in updates:
            task.title = updates["title"]

        if "description" in updates:
            task.description = updates["description"]

        if "status" in updates:
            task.status = TaskStatus(updates["status"])

        if "priority" in updates:
            task.priority = TaskPriority(updates["priority"])

        if "assignee" in updates:
            task.assignee = updates["assignee"]

        self.repo.update(task)
        return "Task updated"

    def assign(self, task_id, assignee):
        task = self.repo.get(task_id)

        if not task:
            return "Task not found"

        task.assignee = assignee
        self.repo.update(task)
        return "Task assigned"

    def delete(self, task_id):
        if self.repo.delete(task_id):
            return "Deleted"
        return "Task not found"

    def search_tasks(self, keyword):
        tasks = self.repo.get_all()
        return self.search.search(tasks, keyword)

    def filter_tasks(self,
                     assignee: Optional[str] = None,
                     status: Optional[str] = None,
                     priority: Optional[str] = None):
        tasks = self.repo.get_all()
        return self.search.filter_tasks(tasks, assignee, status, priority)

    def export_tasks(self, path):
        tasks = self.repo.get_all()
        self.exporter.export(tasks, path)
        return "Tasks exported"

    def reminder(self, task_id):
        task = self.repo.get(task_id)

        if not task:
            return "Task not found"

        self.notifier.remind(task)
        return "Reminder sent"