from models import Task
from task_manager import TaskManager
from components.repository import InMemoryTaskRepository, FileTaskRepository
from components.exporter import JsonExporter, CsvExporter
from components.logger import ConsoleLogger  # Added this import

# Initialize a logger to be used across scenarios
logger = ConsoleLogger()

# Scenario A: In-Memory + JSON + Console Logger
# We now pass THREE dependencies into the constructor
manager_v1 = TaskManager(InMemoryTaskRepository(), JsonExporter(), logger)
manager_v1.add_task(Task(id=1, title="Modular Design", status="In Progress"))
manager_v1.export_tasks("export.json")

print("-" * 30)

# Scenario B: File Storage + CSV + Console Logger
# The TaskManager logic remains identical even with different storage/exporters
manager_v2 = TaskManager(FileTaskRepository(), CsvExporter(), logger)
manager_v2.add_task(Task(id=2, title="Submit Assignment", status="Todo"))
manager_v2.export_tasks("export.csv")