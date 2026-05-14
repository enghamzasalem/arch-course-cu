from models import Task
from components.validator import TaskValidator
from interfaces import ITaskStorage, ITaskExporter
from components.search import TaskSearch
from components.notifier import TaskNotifier

class TaskManager:
    """Main orchestrator for the Task Management System."""
    
    def __init__(
        self, 
        repository: ITaskStorage, 
        exporter: ITaskExporter,
        validator: TaskValidator,
        notifier: TaskNotifier,
        search: TaskSearch
    ):
        self.repository = repository
        self.exporter = exporter
        self.validator = validator
        self.notifier = notifier
        self.search = search
        print("[TaskManager] Initialized with injected components.")

    def create_task(self, task: Task) -> bool:
        """Coordinate task creation."""
        print(f"[TaskManager] Creating task '{task.title}'")
        if self.validator.validate(task):
            self.repository.add(task)
            self.notifier.send_reminder(task)
            return True
        return False

    def list_tasks(self):
        """Coordinate listing tasks."""
        print("[TaskManager] Requesting task list")
        return self.repository.get_all()

    def search_tasks(self, query: str):
        """Coordinate searching tasks."""
        print(f"[TaskManager] Searching tasks for '{query}'")
        return self.search.search(query)

    def export_tasks(self, tasks, format="json"):
        """Coordinate exporting tasks."""
        print(f"[TaskManager] Exporting tasks")
        return self.exporter.export(tasks, format)
