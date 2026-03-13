# Part 1.1 - Component Decomposition
## Task Management System

**Student Name**: Amaan Shaikh
**Submission Date**: 13.03.2026

---

## Components Identified

| Component | Responsibility |
|:----------|:---------------|
| **TaskValidator** | Checks if task data (title, due date) is valid before saving |
| **TaskRepository** | Handles saving, loading, updating, and deleting tasks |
| **TaskSearch** | Filters tasks by assignee, completion status, or text search |
| **TaskExporter** | Converts tasks to JSON or CSV format for export |
| **TaskNotifier** | Checks for upcoming tasks and prints reminders |
| **TaskManager** | Main class that brings everything together |

---

## Why I Chose These Components

I wanted each component to do ONE thing well:

- **TaskValidator** only validates – if validation rules change, only this file changes
- **TaskRepository** only handles storage – can swap memory vs file storage later
- **TaskSearch** only filters tasks – keeps search logic separate from task data
- **TaskExporter** only exports – can add XML exporter later without touching other files
- **TaskNotifier** only sends reminders – can swap console vs email later
- **TaskManager** only orchestrates – knows which component to call for each operation

---

## Module Structure
code/
├── task_manager.py # Main orchestrator
├── models.py # Task class
├── components/
│ ├── validator.py
│ ├── repository.py
│ ├── search.py
│ ├── exporter.py
│ └── notifier.py
└── main.py # Demo


---

## Simple Dependency Graph
        ┌─────────────────┐
        │   TaskManager   │
        └────────┬────────┘
     ┌───────────┼───────────┐
┌─────────┐ ┌──────────┐ ┌─────────┐
│Validator│ │Repository│ │  Search │
└─────────┘ └──────────┘ └─────────┘
                │
          ┌─────┴─────┐
     ┌─────────┐ ┌─────────┐
     │ Exporter│ │ Notifier│
     └─────────┘ └─────────┘

---

## Part 1.2: Interfaces and Dependency Injection (Simple)

**Filename:** `part1_interfaces.md`

```markdown
# Part 1.2 - Interfaces and Dependency Injection
## Task Management System

---

## Interfaces I Used

### 1. ITaskRepository
Any class that handles task storage must have these methods:
- `add(task)` – save a new task
- `get(id)` – find task by id
- `update(task)` – save changes
- `delete(id)` – remove task
- `list_all()` – get all tasks

**Two implementations:**
- `InMemoryRepository` – stores tasks in a dictionary (fast, but lost when program ends)
- `FileRepository` – saves to tasks.json (persists between runs)

### 2. ITaskExporter
Any class that exports tasks must have:
- `export(tasks)` – return tasks as string

**Two implementations:**
- `JsonExporter` – returns JSON format
- `CsvExporter` – returns CSV format

### 3. INotifier
Any class that sends notifications must have:
- `send_reminder(task, message)` – deliver reminder

**One implementation:**
- `ConsoleNotifier` – prints to console

---

## How Dependency Injection Works

Instead of TaskManager creating its own dependencies:

```python
# Bad way - TaskManager creates everything
class TaskManager:
    def __init__(self):
        self.repository = InMemoryRepository()  # Hardcoded!
        self.validator = TaskValidator()