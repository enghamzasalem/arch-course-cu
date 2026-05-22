# Part 1 — Component Decomposition

## Overview

The Task Management System is decomposed into **six components** plus a thin
orchestrator.  Each component has exactly one responsibility.

---

## Component Inventory

| # | Component | Module | Responsibility |
|---|-----------|--------|----------------|
| 1 | **TaskValidator** | `components/validator.py` | Enforce business rules on task data |
| 2 | **TaskRepository** (×2 impls) | `components/repository.py` | Persist and retrieve tasks |
| 3 | **TaskSearch** | `components/search.py` | Filter and search a list of tasks |
| 4 | **TaskExporter** (×2 impls) | `components/exporter.py` | Serialise tasks to JSON or CSV |
| 5 | **TaskNotifier** | `components/notifier.py` | Decide when/how to notify users |
| 6 | **TaskManager** | `task_manager.py` | Coordinate workflows between components |

Supporting files (not components):

- `models.py` — pure data structures (`Task`, `User`, enums).  No logic.
- `interfaces.py` — interface contracts (`ITaskStorage`, `ITaskExporter`).

---

## Component Decomposition with Rationale

### 1. TaskValidator

**Responsibility:** Apply validation rules to a `Task` before it is stored.

**Rationale:**  
Validation rules change for business reasons (new constraints, length limits,
date rules) and must be testable in isolation.  If validation logic lived
inside `TaskManager` or `TaskRepository`, a rule change would require touching
code that should be unrelated to that change.  Isolating it means:
- Rules can be extended or replaced without touching any other component.
- Unit tests for validation require no storage, no search, no I/O.

---

### 2. TaskRepository (InMemoryTaskRepository + FileTaskRepository)

**Responsibility:** Store, retrieve, and delete `Task` objects.

**Rationale:**  
Storage is a classic infrastructure concern that must not pollute business
logic.  By hiding storage behind `ITaskStorage`, we can run tests with
`InMemoryTaskRepository` (fast, no disk I/O) and deploy with
`FileTaskRepository` (persistent) using zero changes to `TaskManager`.  
This is the textbook motivation for the Repository pattern.

---

### 3. TaskSearch

**Responsibility:** Filter a list of tasks by status, priority, assignee, keyword, or tag.

**Rationale:**  
Filtering logic is a distinct concern from storage and orchestration.
It takes a plain list and returns a plain list — no I/O, no side effects.
New filter types (e.g., filter by date range) are added here and nowhere else.

---

### 4. TaskExporter (JsonExporter + CsvExporter)

**Responsibility:** Serialise a list of tasks to an external format.

**Rationale:**  
Export format is an infrastructure/presentation concern.  Business rules do
not care whether the output is JSON or CSV.  The `ITaskExporter` interface
lets us add new formats (e.g., XML, Excel) by writing a new class, not by
modifying existing ones — the Open/Closed principle in practice.

---

### 5. TaskNotifier

**Responsibility:** Evaluate tasks and send reminders for overdue or due-soon tasks.

**Rationale:**  
Notification rules (which tasks trigger an alert, how the message is
formatted, where the message goes) are orthogonal to storage and filtering.
Isolating the notifier means swapping console output for real email/SMS
requires a change in exactly one file.

---

### 6. TaskManager (orchestrator)

**Responsibility:** Coordinate the workflow between components for each use-case.

**Rationale:**  
An orchestrator is needed to handle sequencing: validate → save → notify, etc.
`TaskManager` is kept thin on purpose — it calls components, it never
re-implements their logic.  Its single reason to change is: *the high-level
workflow between components changed* (e.g., a new step is inserted into
"create task").

---

## Module Structure

```
code/
├── models.py                  # Data containers — no logic
├── interfaces.py              # ITaskStorage, ITaskExporter protocols
├── task_manager.py            # Orchestrator (receives all deps via constructor)
├── main.py                    # Runnable demo
└── components/
    ├── __init__.py
    ├── validator.py           # TaskValidator
    ├── repository.py          # InMemoryTaskRepository, FileTaskRepository
    ├── search.py              # TaskSearch
    ├── exporter.py            # JsonExporter, CsvExporter
    └── notifier.py            # TaskNotifier
```
