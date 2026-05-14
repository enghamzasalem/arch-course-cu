from models import Task, TaskStatus, TaskPriority
from task_manager import TaskManager
from components.repository import InMemoryTaskRepository, FileTaskRepository
from components.exporter import JsonExporter, CsvExporter
from components.validator import TaskValidator
from components.notifier import TaskNotifier
from components.search import TaskSearch

def run_demo(manager: TaskManager, config_name: str):
    print(f"\n--- Running Demo with {config_name} ---")
    
    # Create a task
    new_task = Task(
        id="1",
        title="Implement Task",
        description="Modular component decomposition.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH
    )
    
    print("\n1. Creating Task:")
    manager.create_task(new_task)
    
    print("\n2. Searching Tasks:")
    manager.search_tasks("Task")
    
    print("\n3. Listing Tasks:")
    manager.list_tasks()
    
    print("\n4. Exporting Tasks:")
    manager.export_tasks([new_task])
    
def main():
    """Demo usage of Dependency Injection."""
    print("--- Task Management System DI Demo ---")
    
    # Shared components
    validator = TaskValidator()
    notifier = TaskNotifier()
    search = TaskSearch()
    
    # Configuration 1: InMemoryTaskRepository + JsonExporter
    print("\nConfiguration 1: InMemoryTaskRepository + JsonExporter")
    repo1 = InMemoryTaskRepository()
    exporter1 = JsonExporter()
    manager1 = TaskManager(repo1, exporter1, validator, notifier, search)
    run_demo(manager1, "Configuration 1")
    
    # Configuration 2: FileTaskRepository + CsvExporter
    print("\n" + "="*40)
    print("Configuration 2: FileTaskRepository + CsvExporter")
    repo2 = FileTaskRepository()
    exporter2 = CsvExporter()
    manager2 = TaskManager(repo2, exporter2, validator, notifier, search)
    run_demo(manager2, "Configuration 2")
    
    print("\n--- DI Demo Completed ---")

if __name__ == "__main__":
    main()
