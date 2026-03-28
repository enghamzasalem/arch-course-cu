# Part 1.1 – Component Decomposition (Task Management System)

## System Overview

The **Task Management System** supports:

- Creating, updating, and deleting tasks
- Assigning tasks to users
- Filtering and searching tasks
- Exporting tasks to JSON/CSV
- Sending (simulated) console reminders

Implementation lives under `code/`.

## Components and Responsibilities (5+)

### 1. TaskManager (orchestrator)

- **Responsibility**: Coordinate use cases: create/update/delete tasks, reassign, list, search, export, send reminders.
- **Why SRP**: Orchestrates only; delegates validation, persistence, and export to other components. Search and reminder logic live here to keep the submission minimal.
- **Key methods**: `create_task`, `update_status`, `reassign`, `delete_task`, `list_tasks`, `search_tasks`, `export_tasks`, `send_reminders_for_assignee`.

### 2. TaskValidator

- **Responsibility**: Validate task data and status transitions.
- **Why SRP**: Only checks rules (non-empty title, no transition from DONE back).
- **Methods**: `validate_new_task`, `validate_status_transition`.

### 3. InMemoryTaskRepository / FileTaskRepository

- **Responsibility**: Persist and retrieve `Task` entities.
- **Why SRP**: Storage only; no business logic or validation.
- **Implementations**: In-memory dict; file-based JSON.
- **Interface (ITaskStorage)**: `add`, `get`, `list_all`, `update`, `delete`, `find_by_assignee`.

### 4. JsonTaskExporter / CsvTaskExporter

- **Responsibility**: Export tasks to external formats.
- **Why SRP**: Only convert tasks to JSON or CSV.
- **Interface (ITaskExporter)**: `export(tasks, destination)`.

## Rationale

- **Separation of concerns**: Validation, storage, and export are separate; TaskManager composes them.
- **SRP**: Each component has one reason to change (e.g. validation rules, storage backend, export format).
- **DI**: TaskManager receives `ITaskStorage` and `ITaskExporter` via constructor; implementations can be swapped (see `main.py`).
