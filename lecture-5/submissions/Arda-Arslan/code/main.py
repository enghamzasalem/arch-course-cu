from task_manager import TaskManager

from components.repository import InMemoryTaskRepository, FileTaskRepository
from components.validator import TaskValidator
from components.search import TaskSearch
from components.exporter import JsonExporter, CsvExporter
from components.notifier import TaskNotifier


def print_tasks(tasks, text):
    print(text)
    for t in tasks:
        print(f"{t.id} - {t.title} - {t.status.value} - {t.priority.value} - {t.assignee}")
    print()


def run_memory_version():
    manager = TaskManager(
        InMemoryTaskRepository(),
        TaskValidator(),
        TaskSearch(),
        JsonExporter(),
        TaskNotifier()
    )

    print(manager.create({
        "id": "1",
        "title": "Finish assignment",
        "priority": "high",
        "assignee": "John"
    }))

    print(manager.create({
        "id": "2",
        "title": "Prepare slides",
        "description": "Slides for team meeting",
        "priority": "medium"
    }))

    print(manager.update("2", {"status": "in_progress"}))
    print(manager.assign("2", "John"))

    found = manager.search_tasks("finish")
    print_tasks(found, "search result:")

    filtered = manager.filter_tasks(assignee="John")
    print_tasks(filtered, "filtered by assignee:")

    print(manager.export_tasks("tasks.json"))
    print(manager.reminder("1"))

    print(manager.delete("2"))


def run_file_version():
    manager = TaskManager(
        FileTaskRepository("tasks_storage.json"),
        TaskValidator(),
        TaskSearch(),
        CsvExporter(),
        TaskNotifier()
    )

    print(manager.create({
        "id": "3",
        "title": "Fix login bug",
        "description": "Investigate authentication issue",
        "priority": "low",
        "assignee": "John"
    }))

    all_tasks = manager.filter_tasks()
    print_tasks(all_tasks, "tasks in file repository:")

    print(manager.export_tasks("tasks.csv"))
    print(manager.reminder("3"))


if __name__ == "__main__":
    run_memory_version()
    run_file_version()