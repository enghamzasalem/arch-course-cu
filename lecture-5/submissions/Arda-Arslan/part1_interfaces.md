# Task 1.2 – Interfaces and Dependency Injection

## Interfaces Used

In the system, I defined two interfaces:

- ITaskRepository
- ITaskExporter

These interfaces were created using Protocol.

---

## ITaskRepository

The ITaskRepository interface defines the basic operations for storing and managing tasks.

Methods included:

- add(task)
- get(task_id)
- get_all()
- update(task)
- delete(task_id)

### Implementations

Two repository implementations were created:

1. **InMemoryTaskRepository**  
   This version stores tasks in a Python dictionary.  
   It is simple and useful for testing or small examples.

2. **FileTaskRepository**  
   This version stores tasks in a JSON file.  
   It allows data to stay available after the program stops.

Because both classes follow the same interface, they can be swapped without changing the TaskManager.

---

## ITaskExporter

The ITaskExporter interface defines how task data is exported.

Method included:

- export(tasks, path)

### Implementations

Two exporter implementations were created:

1. **JsonExporter**  
   Exports task data in JSON format.

2. **CsvExporter**  
   Exports task data in CSV format.

This makes the system more flexible because the export format can be changed easily.

---

## Dependency Injection

Dependency injection was used in the TaskManager constructor.

The TaskManager receives its dependencies from outside instead of creating them inside the class.

Example:
```python
manager = TaskManager(
    InMemoryTaskRepository(),
    TaskValidator(),
    TaskSearch(),
    JsonExporter(),
    TaskNotifier()
)
```
---

## Swapping Implementations

One advantage of this approach is that implementations can be changed without modifying the TaskManager.

For example, the repository and exporter can be swapped like this:
```python
manager = TaskManager(
    FileTaskRepository("tasks_storage.json"),
    TaskValidator(),
    TaskSearch(),
    CsvExporter(),
    TaskNotifier()
)
```