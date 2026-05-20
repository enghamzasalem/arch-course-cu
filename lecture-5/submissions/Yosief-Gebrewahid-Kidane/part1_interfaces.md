# Task 1.2 – Interfaces and Dependency Injection

## Overview

To achieve low coupling and flexible architecture, the Task Management System uses **interfaces** and **dependency injection**. Interfaces define contracts that components must follow, while dependency injection allows the main system to receive implementations from outside instead of creating them internally.

Two main interfaces are used in this system:

- `ITaskRepository`
- `ITaskExporter`


---

## ITaskRepository Interface


The `ITaskRepository` interface defines how tasks are stored and retrieved.  
By using this interface, the system does not depend on a specific storage implementation.

### Interface Definition

class ITaskRepository(Protocol):
    def add(self, task: Task) -> None: ...
    def get(self, task_id: str) -> Task: ...
    def list(self) -> List[Task]: ...
    def delete(self, task_id: str) -> None: ...


### Implementations

#### InMemoryTaskRepository

This implementation stores tasks in memory using a Python dictionary. 
It is Simple, Fast, and No external storage required.



#### FileTaskRepository

This implementation stores tasks in a file (for example JSON format).
It is Persistent storage and Data is saved even after the program stops.

---

## ITaskExporter Interface

The `ITaskExporter` interface defines how tasks are exported to external formats.

### Interface Definition

class ITaskExporter(Protocol):
    def export(self, tasks: List[Task], filepath: str) -> None: ...


### Implementations

#### JsonExporter

Exports tasks to JSON format.
It is Human readable, Common format for data exchange, and Easy integration with web systems.



#### CsvExporter

Exports tasks to CSV format.
It is Compatible with spreadsheet applications, and Lightweight and simple format.

---

## Dependency Injection

The `TaskManager` receives its dependencies through its constructor instead of creating them internally.

class TaskManager:

    def __init__(self, repository, exporter):
        self.repository = repository
        self.exporter = exporter


Dependencies are injected when the system is created:


repository = InMemoryTaskRepository()
exporter = JsonExporter()

manager = TaskManager(repository, exporter)


---

## Swapping Implementations

Because the system depends on interfaces rather than concrete implementations, implementations can be easily swapped without modifying the `TaskManager`.

Using JSON exporter


exporter = JsonExporter()
manager = TaskManager(repository, exporter)


Switching to CSV exporter:


exporter = CsvExporter()
manager = TaskManager(repository, exporter)


Similarly, the repository implementation can be changed:


repository = FileTaskRepository("tasks.json")
manager = TaskManager(repository, exporter)


The `TaskManager` code remains unchanged, demonstrating **low coupling**.

---

## Benefits of Interfaces and Dependency Injection

Using interfaces and dependency injection provides several benefits:

- **Low coupling** between system components
- **Flexibility** to change implementations easily
- **Better maintainability**
- **Improved testability** using mock implementations
- **Extensibility** for adding new storage or export formats


