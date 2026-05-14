from task_manager import TaskManager
from components.repository import InMemoryTaskRepository
from components.exporter import JsonExporter
from models import Task

def main():

    # Inject dependencies
    repository = InMemoryTaskRepository()
    exporter = JsonExporter()

    manager = TaskManager(repository, exporter)

    # Create tasks
    task1 = Task(1, "Write report", "Write project report", "Alice")
    task2 = Task(2, "Prepare slides", "Slides for presentation", "Bob")

    manager.create_task(task1)
    manager.create_task(task2)

    # Display tasks
    print("All Tasks:")
    for task in manager.get_tasks():
        print(task)

    # Search tasks
    print("\nSearch 'write':")
    results = manager.search_tasks("write")
    for task in results:
        print(task)

    # Export tasks
    manager.export_tasks("tasks.json")

    # Send reminders
    manager.send_reminders()


if __name__ == "__main__":
    main()