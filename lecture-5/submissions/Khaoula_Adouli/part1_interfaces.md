# Part 1 – Interfaces and Dependency Injection
 
## Overview
 
This system uses interface-based design to reduce coupling between components.  

Interfaces define contracts that allow different implementations of the same functionality.
 
By relying on interfaces instead of concrete implementations, the system becomes more flexible and easier to extend.
 
---
 
# Repository Interface
 
## ITaskRepository
 
The `ITaskRepository` interface defines the contract for storing and retrieving tasks.
 
Main responsibilities:
 
- Add a task

- Update a task

- Delete a task

- Retrieve a task by ID

- Retrieve all tasks
 
Two implementations of this interface are provided:
 
### InMemoryTaskRepository
 
This implementation stores tasks in memory using a list.  

It is simple and useful for testing or temporary storage.
 
### FileTaskRepository
 
This implementation stores tasks in a JSON file.  

It allows tasks to persist between application runs.
 
Using an interface allows the system to switch between these implementations without modifying the `TaskManager`.
 
---
 
# Exporter Interface
 
## ITaskExporter
 
The `ITaskExporter` interface defines how tasks are exported to external formats.
 
Main responsibility:
 
- Export tasks to a file
 
Two implementations are provided:
 
### JsonExporter
 
Exports tasks to a JSON file.
 
### CsvExporter
 
Exports tasks to a CSV file.
 
Because both exporters follow the same interface, the export format can be changed without modifying the core system.
 
---
 
# Dependency Injection
 
The `TaskManager` uses dependency injection to receive its dependencies.
 
Instead of creating components internally, the `TaskManager` receives them through its constructor.
 
Example:
 
TaskManager(repository, validator, search, exporter, notifier)
 
This design allows different implementations to be injected at runtime.
 
For example:
 
- InMemoryTaskRepository can be replaced by FileTaskRepository

- JsonExporter can be replaced by CsvExporter
 
without changing the TaskManager code.
 
---
 
# Benefits of This Design
 
Using interfaces and dependency injection provides several advantages:
 
- **Low Coupling** – Components depend on interfaces rather than concrete implementations.

- **Flexibility** – Implementations can be easily replaced.

- **Testability** – Components can be tested independently.

- **Extensibility** – New implementations can be added without modifying existing code.
 