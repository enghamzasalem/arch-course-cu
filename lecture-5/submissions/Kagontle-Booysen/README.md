# Task Management System

A modular Python application demonstrating **separation of concerns**, **Protocol-based interfaces**, and **constructor dependency injection** — built as a practical implementation of Chapter 5: Modularity and Components.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Components](#components)
- [Interfaces](#interfaces)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Swapping Implementations](#swapping-implementations)
- [Data Model](#data-model)
- [Design Decisions](#design-decisions)
- [Deliverables](#deliverables)

---

## Overview

The Task Management System lets you create, update, delete, and assign tasks to users — with filtering, search, multi-format export, and reminder notifications. Every capability is implemented as an independent, swappable component behind a typed interface.

**Key capabilities:**

| Feature | Detail |
|---------|--------|
| Task CRUD | Create, read, update, delete tasks |
| Assignment | Assign tasks to registered users |
| Search & filter | Keyword search; filter by status, priority, assignee, tag, due date |
| Export | JSON (pretty-printed) or CSV (RFC 4180) |
| Notifications | Console output or timestamped log file |
| Storage | In-memory (fast, ephemeral) or JSON file (persistent) |

**Design principles applied:**

- **Single Responsibility Principle** — each component has exactly one reason to change
- **Dependency Inversion Principle** — `TaskManager` depends on abstractions, never concrete classes
- **Open/Closed Principle** — new storage backends, export formats, or notification channels require zero changes to existing code
- **Low coupling** — no concrete class imports another concrete class
- **High cohesion** — every method in a component serves its single stated purpose

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client / Application                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       TaskManager                               │
│              Orchestrator · Façade · DI wiring                  │
└───┬──────────────┬──────────────┬──────────────┬───────────┬───┘
    │ «inject»     │ «inject»     │ «inject»     │ «inject»  │ «inject»
    ▼              ▼              ▼              ▼           ▼
ITaskStorage  ITaskExporter  ITaskNotifier  ITaskSearch  ITaskValidator
    │              │              │              │           │
    ├─ InMemory    ├─ Json        ├─ Console     └─ TaskSearch└─ TaskValidator
    └─ File        └─ Csv         └─ LogFile
                           │
                           ▼
                       models.py
               Task · User · Priority · Status
```

`TaskManager` depends only on the five interfaces. Every interface has at least two concrete implementations. Swapping an implementation requires changing **one constructor argument** — no `TaskManager` code changes.

See [`part2_component_diagram.png`](part2_component_diagram.png) for the full visual diagram, or open [`part2_component_diagram.html`](part2_component_diagram.html) for the interactive version.

---

## Project Structure

```
.
├── README.md
├── code/
│   ├── task_manager.py              # Orchestrator — entry point
│   ├── interfaces.py                # Protocol definitions (all 5 interfaces)
│   ├── models.py                    # Data structures: Task, User, enums
│   └── components/
│       ├── __init__.py              # Package exports
│       ├── repository.py            # InMemoryTaskRepository + FileTaskRepository
│       ├── json_exporter.py         # JsonExporter
│       ├── csv_exporter.py          # CsvExporter
│       ├── console_notifier.py      # ConsoleNotifier
│       ├── log_notifier.py          # LogFileNotifier
│       ├── search.py                # TaskSearch
│       └── validator.py             # TaskValidator
├── part2_component_diagram.png      # Architecture diagram
├── part2_component_diagram.drawio   # Editable diagram source
├── part2_component_diagram.html     # Interactive diagram
├── part2_cohesion_coupling.md       # Cohesion & coupling analysis
├── part1_component_design.md        # Component decomposition rationale
└── part1_interfaces.md              # Interface design rationale
```

---

## Components

### `TaskManager` — Orchestrator

**File:** `code/task_manager.py`

The single public API surface. Accepts all five dependencies via constructor injection and delegates every operation to the appropriate component. Contains no business logic of its own.

```python
from task_manager import TaskManager

tm = TaskManager()  # all defaults wired automatically
```

Or with explicit injection:

```python
tm = TaskManager(
    storage   = FileTaskRepository("tasks.json"),
    exporter  = CsvExporter(),
    notifier  = LogFileNotifier("notifications.log"),
)
```

---

### Storage — `ITaskStorage`

**File:** `code/components/repository.py`

| Class | Backend | When to use |
|-------|---------|-------------|
| `InMemoryTaskRepository` | Python `dict` | Tests, scripts, single-session apps |
| `FileTaskRepository` | JSON file on disk | Apps that need data to survive restarts |

Both expose identical CRUD methods: `add`, `get`, `update`, `delete`, `list_all`, `assign`, `count`.

---

### Export — `ITaskExporter`

| Class | File | Output |
|-------|------|--------|
| `JsonExporter` | `json_exporter.py` | Pretty-printed JSON array |
| `CsvExporter` | `csv_exporter.py` | RFC 4180 CSV with header row |

Both expose `export(tasks, filepath)`, `to_string(tasks)`, and `format_name`.

---

### Notifications — `ITaskNotifier`

| Class | File | Channel |
|-------|------|---------|
| `ConsoleNotifier` | `console_notifier.py` | `stdout` (or any injected callable) |
| `LogFileNotifier` | `log_notifier.py` | Append-only timestamped log file |

Both expose `send_reminders(tasks, window_hours)` and `send_assignment_notice(task, user_name)`.

---

### Search — `ITaskSearch`

**File:** `code/components/search.py` · Class: `TaskSearch`

Pure functions — no I/O, no state, no side effects.

| Method | Description |
|--------|-------------|
| `filter(tasks, **criteria)` | Filter by `status`, `priority`, `assigned_to`, `tag`, `due_before`, `due_after` |
| `search(tasks, keyword)` | Case-insensitive substring match on title + description |
| `sort(tasks, by, descending)` | Sort by any task field; handles `None` due dates gracefully |

---

### Validation — `ITaskValidator`

**File:** `code/components/validator.py` · Class: `TaskValidator`

Validates raw `dict` payloads before they reach the storage layer.

| Method | Description |
|--------|-------------|
| `validate_new(data)` | Checks all required fields for a new task |
| `validate_update(data)` | Checks only the fields present in a partial-update dict |

Raises `ValidationError(field, message)` on the first invalid field.

---

## Interfaces

**File:** `code/interfaces.py`

All interfaces use `typing.Protocol` with `@runtime_checkable`. This means:

- **No inheritance required** — any class with the right methods satisfies the interface automatically (structural / duck typing)
- **Statically checkable** — mypy and Pyright verify conformance at type-check time
- **Runtime verifiable** — `isinstance(obj, ITaskStorage)` works at runtime

```python
from interfaces import ITaskStorage, ITaskExporter, ITaskNotifier

# Runtime conformance check
assert isinstance(InMemoryTaskRepository(), ITaskStorage)  # True
assert isinstance(FileTaskRepository("x.json"), ITaskStorage)  # True
assert isinstance(JsonExporter(), ITaskExporter)             # True
assert isinstance(CsvExporter(), ITaskExporter)              # True
```

---

## Quick Start

**Requirements:** Python 3.10+ · No external dependencies · stdlib only

```bash
# Clone / unzip the project
cd code/

# Run the built-in demo (4 scenarios)
python task_manager.py
```

The demo runs four scenarios end-to-end:
1. Default wiring — InMemory storage, JSON export, Console notifications
2. File storage + CSV export (TaskManager code unchanged)
3. LogFile notifier — notifications written to a file
4. Runtime Protocol conformance check for all 6 implementations

Expected output:

```
==============================================================
  Scenario 1: InMemoryRepository + JsonExporter + ConsoleNotifier
==============================================================
[Console] ASSIGNMENT — 'Design database schema' assigned to Alice.
[Console] ASSIGNMENT — 'Write unit tests' assigned to Bob.
Active exporter : JSON
Tasks stored    : 3
...
  Scenario 4: Runtime Protocol conformance verification
==============================================================
  ✔ PASS  InMemoryTaskRepository          satisfies  ITaskStorage
  ✔ PASS  FileTaskRepository              satisfies  ITaskStorage
  ✔ PASS  JsonExporter                    satisfies  ITaskExporter
  ✔ PASS  CsvExporter                     satisfies  ITaskExporter
  ✔ PASS  ConsoleNotifier                 satisfies  ITaskNotifier
  ✔ PASS  LogFileNotifier                 satisfies  ITaskNotifier
```

---

## Usage Guide

All examples assume you are inside the `code/` directory.

### Create tasks and users

```python
from task_manager import TaskManager

tm = TaskManager()

# Register users
alice = tm.register_user("Alice", "alice@example.com")
bob   = tm.register_user("Bob",   "bob@example.com")

# Create a task
task = tm.create_task(
    title       = "Design database schema",
    description = "ERD + migration scripts for v2",
    priority    = "high",               # low | medium | high | critical
    status      = "todo",               # todo | in_progress | done | cancelled
    due_date    = "2025-06-01T09:00:00",  # ISO 8601, optional
    tags        = ["backend", "db"],      # optional
)

print(task.task_id)   # auto-generated UUID
print(task.priority)  # Priority.HIGH
```

### Assign, update, delete

```python
# Assign task to a user (triggers assignment notification)
tm.assign_task(task.task_id, alice.user_id)

# Partial update — only supply the fields you want to change
tm.update_task(task.task_id, status="in_progress")
tm.update_task(task.task_id, priority="critical", title="Redesign schema")

# Delete
tm.delete_task(task.task_id)
```

### Search and filter

```python
# Keyword search (title + description)
results = tm.search_tasks("schema")

# Filter — combine any criteria, all are optional
high_priority = tm.filter_tasks(priority="high")
alices_tasks  = tm.filter_tasks(assigned_to=alice.user_id)
due_soon      = tm.filter_tasks(
    status     = "todo",
    due_before = "2025-07-01T00:00:00",
)
tagged        = tm.filter_tasks(tag="backend")

# Sort
by_priority = tm.sort_tasks(by="priority", descending=True)
by_due_date = tm.sort_tasks(by="due_date")
```

### Export

```python
# Export using the configured exporter (JSON by default)
tm.export_tasks("output/tasks.json")

# Get as string (no file I/O)
json_string = tm.export_to_string()

# See which format is active
print(tm.export_format)  # "JSON"
```

### Send reminders

```python
# Remind about tasks due within the next 48 hours
messages = tm.send_reminders(window_hours=48)

# Returns a list of the messages emitted:
# "[Console] OVERDUE  — 'Design database schema' was due 2025-06-01..."
# "[Console] UPCOMING — 'Fix login bug' due in ~3h | priority: critical"
```

---

## Swapping Implementations

`TaskManager` accepts any conforming implementation via constructor injection. The class itself never changes — only what you pass in.

### Persistent storage (file-backed)

```python
from task_manager import TaskManager
from components import FileTaskRepository

tm = TaskManager(storage=FileTaskRepository("my_tasks.json"))
# Tasks are now saved to disk and survive process restarts
```

### CSV export

```python
from components import CsvExporter

tm = TaskManager(exporter=CsvExporter())
tm.export_tasks("report.csv")   # writes RFC 4180 CSV
print(tm.export_format)         # "CSV"
```

### Production logging

```python
from components import LogFileNotifier

tm = TaskManager(notifier=LogFileNotifier("notifications.log"))
tm.send_reminders()
# Appends to notifications.log:
# 2025-06-01T09:00:00Z  [LogFile] OVERDUE  — 'Design schema' ...
```

### Full production stack

```python
from task_manager import TaskManager
from components import FileTaskRepository, CsvExporter, LogFileNotifier

tm = TaskManager(
    storage  = FileTaskRepository("prod_tasks.json"),
    exporter = CsvExporter(delimiter=","),
    notifier = LogFileNotifier("prod_notifications.log"),
)
# TaskManager source code: zero changes
```

### Test double — capture notifications without stdout

```python
captured = []

tm = TaskManager(
    storage  = InMemoryTaskRepository(),
    notifier = ConsoleNotifier(output_sink=captured.append),
)
tm.send_reminders()
assert "[Console] OVERDUE" in captured[0]
```

### Bring your own implementation

Any class that has the right methods satisfies the interface — no inheritance needed:

```python
class RedisTaskRepository:
    def add(self, task): ...
    def get(self, task_id): ...
    def update(self, task_id, updates): ...
    def delete(self, task_id): ...
    def list_all(self): ...
    def assign(self, task_id, user_id): ...
    def count(self): ...

tm = TaskManager(storage=RedisTaskRepository())  # works immediately
```

---

## Data Model

### `Task`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Auto | UUID generated on creation |
| `title` | `str` | ✅ | Short task title |
| `description` | `str` | ✅ | Detailed description |
| `priority` | `Priority` | ✅ | `low` · `medium` · `high` · `critical` |
| `status` | `Status` | ✅ | `todo` · `in_progress` · `done` · `cancelled` |
| `due_date` | `datetime` | — | ISO 8601 string at creation; `datetime` in memory |
| `assigned_to` | `str` | — | `user_id` of assigned user |
| `tags` | `list[str]` | — | Arbitrary string tags |
| `created_at` | `datetime` | Auto | UTC timestamp on creation |
| `updated_at` | `datetime` | Auto | UTC timestamp on last update |

### `User`

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `str` | UUID generated by `register_user()` |
| `name` | `str` | Display name |
| `email` | `str` | Email address |

### Enumerations

```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
```

---

## Design Decisions

### Why `typing.Protocol` instead of ABC?

Abstract Base Classes require explicit inheritance (`class Foo(IStorage): ...`). Protocols are *structural* — a class satisfies an interface simply by having the right methods. This means third-party classes or legacy code can satisfy an interface without being modified. It also avoids the diamond inheritance problems that emerge with deep ABC hierarchies.

### Why constructor injection instead of a DI framework?

The system is deliberately dependency-free (stdlib only). Constructor injection — passing dependencies in as arguments — achieves full testability and swappability without adding a framework like `injector` or `dependency-injector`. Every component can be instantiated and tested with a single `ClassName()` call.

### Why are `TaskSearch` methods pure functions?

`TaskSearch` receives a `list[Task]` and returns a `list[Task]`. It holds no reference to the storage layer and produces no side effects. This means it can be tested with any hand-crafted list, used in memory-only pipelines, and reasoned about without understanding the rest of the system. The coupling to the rest of the system is limited to the `Task` type.

### Why split `ConsoleNotifier` and `LogFileNotifier` into separate classes?

Both notify — but their *output channel* is different, and channels change independently. Adding structured JSON log output to `LogFileNotifier` should not affect `ConsoleNotifier` behaviour. Keeping them separate follows SRP: each has one reason to change (its output format / channel), and a test that verifies console output doesn't need to care about file I/O.

For a full cohesion, coupling, and SRP analysis see [`part2_cohesion_coupling.md`](part2_cohesion_coupling.md).

---

## Deliverables

| File | Description |
|------|-------------|
| `code/task_manager.py` | Orchestrator, DI wiring, runnable demo |
| `code/interfaces.py` | All 5 Protocol interface definitions |
| `code/models.py` | Task, User, Priority, Status data structures |
| `code/components/repository.py` | InMemoryTaskRepository + FileTaskRepository |
| `code/components/json_exporter.py` | JsonExporter |
| `code/components/csv_exporter.py` | CsvExporter |
| `code/components/console_notifier.py` | ConsoleNotifier |
| `code/components/log_notifier.py` | LogFileNotifier |
| `code/components/search.py` | TaskSearch |
| `code/components/validator.py` | TaskValidator |
| `code/part1_component_design.md` | Component decomposition rationale |
| `code/part1_interfaces.md` | Interface design rationale |
| `part2_component_diagram.png` | Architecture diagram (PNG) |
| `part2_component_diagram.drawio` | Editable diagram source |
| `part2_component_diagram.html` | Interactive diagram (browser) |
| `part2_cohesion_coupling.md` | Full cohesion, coupling, SRP analysis |
