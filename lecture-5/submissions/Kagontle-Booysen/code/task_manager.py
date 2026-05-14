from models import Task
from components.validator import TaskValidator
from components.repository import TaskRepository
from components.search import TaskSearch
from components.exporter import TaskExporter
from components.notifier import TaskNotifier


class TaskManager:
    def __init__(self):
        self.validator = TaskValidator()
        self.repository = TaskRepository()
        self.search = TaskSearch()
        self.exporter = TaskExporter()
        self.notifier = TaskNotifier()

    def create_task(self, task_id, title, description, assigned_to=None, status="Pending"):
        self.validator.validate_task_data(task_id, title, description, assigned_to, status)
        task = Task(task_id, title, description, assigned_to, status)
        self.repository.add(task)
        return task

    def update_task(self, task_id, title=None, description=None, assigned_to=None, status=None):
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id {task_id} not found.")

        new_title = title if title is not None else task.title
        new_description = description if description is not None else task.description
        new_assigned_to = assigned_to if assigned_to is not None else task.assigned_to
        new_status = status if status is not None else task.status

        self.validator.validate_task_data(
            task_id,
            new_title,
            new_description,
            new_assigned_to,
            new_status
        )

        updated_task = Task(task_id, new_title, new_description, new_assigned_to, new_status)
        self.repository.update(updated_task)
        return updated_task

    def delete_task(self, task_id):
        self.repository.delete(task_id)

    def assign_task(self, task_id, username):
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id {task_id} not found.")
        return self.update_task(task_id, assigned_to=username)

    def get_all_tasks(self):
        return self.repository.get_all()

    def search_tasks_by_title(self, keyword):
        return self.search.search_by_title(self.repository.get_all(), keyword)

    def filter_tasks_by_status(self, status):
        return self.search.filter_by_status(self.repository.get_all(), status)

    def filter_tasks_by_user(self, username):
        return self.search.filter_by_assigned_user(self.repository.get_all(), username)

    def export_tasks_json(self, filename):
        self.exporter.export_to_json(self.repository.get_all(), filename)

    def export_tasks_csv(self, filename):
        self.exporter.export_to_csv(self.repository.get_all(), filename)

    def send_task_reminder(self, task_id):
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task with id {task_id} not found.")
        self.notifier.send_reminder(task)
