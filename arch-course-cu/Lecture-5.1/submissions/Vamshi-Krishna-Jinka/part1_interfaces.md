# Task 1.2 – Interfaces and Dependency Injection

## Interfaces Used

### 1. ITaskStorage

Purpose:
Defines the contract for task storage implementations.

Methods:

add_task(task)
get_tasks()
delete_task(task_id)

Implementations:

InMemoryTaskRepository
FileTaskRepository (can be added later)

Benefit:
TaskManager does not depend on a specific storage implementation.

---

### 2. ITaskExporter

Purpose:
Defines how tasks are exported.

Method:

export(tasks, filename)

Implementations:

JsonExporter
CsvExporter

Benefit:
Export format can be changed without modifying TaskManager.

---

## Dependency Injection

TaskManager receives dependencies through its constructor.

Example:

TaskManager(repository, exporter)

This means the manager does not create the dependencies itself.

Example usage:
