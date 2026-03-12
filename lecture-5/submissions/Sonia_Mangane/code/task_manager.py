from typing import List
from models import Task
from components.repository import ITaskRepository
from components.exporter import ITaskExporter
from components.logger import ILogger

class TaskManager:
    def __init__(self, repository: ITaskRepository, exporter: ITaskExporter, logger: ILogger):
        self.repository = repository
        self.exporter = exporter
        self.logger = logger

    def add_task(self, task):
        self.logger.log(f"Attempting to add task: {task.title}")
        self.repository.add(task)
        self.logger.log("Task successfully added.")

    def export_tasks(self, path: str):
        tasks = self.repository.get_all()
        self.exporter.export(tasks, path)