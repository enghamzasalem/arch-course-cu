# Part 1 — Task 1.2: Interfaces and Dependency Injection

## 1. Overview

Task 1.2 adds a formal interface layer on top of the components built in Task 1.1.
Interfaces are defined using Python's `typing.Protocol` (PEP 544), and every
dependency in `TaskManager` is now accepted as an interface type rather than a
concrete class.

### Updated module structure

```
code/
├── interfaces.py                  ← NEW  — all Protocol definitions
├── task_manager.py                ← UPDATED — typed against interfaces; full DI demo
├── models.py
└── components/
    ├── repository.py              ← UPDATED — two ITaskStorage implementations
    │     InMemoryTaskRepository
    │     FileTaskRepository
    ├── json_exporter.py           ← NEW — ITaskExporter / JSON
    ├── csv_exporter.py            ← NEW — ITaskExporter / CSV
    ├── console_notifier.py        ← NEW — ITaskNotifier / stdout
    ├── log_notifier.py            ← NEW — ITaskNotifier / log file
    ├── validator.py               (unchanged — implicitly satisfies ITaskValidator)
    ├── search.py                  (unchanged — implicitly satisfies ITaskSearch)
    └── __init__.py                ← UPDATED
```

---

## 2. Interfaces Defined

All five interfaces live in `interfaces.py` and use `@runtime_checkable Protocol`,
which means conformance can be verified both statically (mypy) and at runtime
(`isinstance(obj, ITaskStorage)`).

### 2.1 `ITaskStorage`

```python
class ITaskStorage(Protocol):
    def add(self, task: Task) -> Task: ...
    def get(self, task_id: str) -> Task: ...
    def update(self, task_id: str, updates: dict) -> Task: ...
    def delete(self, task_id: str) -> None: ...
    def list_all(self) -> list[Task]: ...
    def assign(self, task_id: str, user_id: Optional[str]) -> Task: ...
    def count(self) -> int: ...
```

**Purpose:** Abstracts any persistence backend behind a uniform CRUD API.
`TaskManager` never knows whether tasks are held in memory, a JSON file,
a SQL database, or a cloud store.

**Implementations:**

| Class | Backend | Persistence | Notes |
|-------|---------|-------------|-------|
| `InMemoryTaskRepository` | Python `dict` | Process lifetime only | Fast; ideal for tests |
| `FileTaskRepository` | JSON file on disk | Survives restarts | Human-readable; no DB needed |

### 2.2 `ITaskExporter`

```python
class ITaskExporter(Protocol):
    def export(self, tasks: list[Task], filepath: str) -> str: ...
    def to_string(self, tasks: list[Task]) -> str: ...
    @property
    def format_name(self) -> str: ...
```

**Purpose:** Abstracts the serialisation format. `TaskManager.export_tasks()`
calls `self._exporter.export(...)` without knowing whether the output will be
JSON, CSV, XML, or any future format.

**Implementations:**

| Class | Format | Key behaviour |
|-------|--------|---------------|
| `JsonExporter` | JSON | Pretty-printed array; configurable indent |
| `CsvExporter`  | CSV  | RFC 4180; list fields flattened to `;`-separated strings |

### 2.3 `ITaskNotifier`

```python
class ITaskNotifier(Protocol):
    def send_reminders(self, tasks: list[Task], window_hours: int = 24) -> list[str]: ...
    def send_assignment_notice(self, task: Task, user_name: str) -> str: ...
```

**Purpose:** Decouples notification delivery from the rest of the system.
Swapping from console output to email, Slack, or a log file requires only
changing the injected object — no `TaskManager` code changes.

**Implementations:**

| Class | Channel | Notes |
|-------|---------|-------|
| `ConsoleNotifier` | `stdout` (configurable sink) | Development / demo use |
| `LogFileNotifier` | Append-only log file | Timestamped; production-style audit trail |

### 2.4 `ITaskSearch` and `ITaskValidator`

The existing `TaskSearch` and `TaskValidator` classes from Task 1.1 already
satisfy these Protocols structurally — no code changes were required.
Their interfaces are formalised here for documentation completeness and
to enable future alternative implementations (e.g. a database-backed
full-text search engine, or a schema-based validator using Pydantic).

---

## 3. Dependency Injection in `TaskManager`

```python
class TaskManager:
    def __init__(
        self,
        storage:   Optional[ITaskStorage]   = None,
        exporter:  Optional[ITaskExporter]  = None,
        notifier:  Optional[ITaskNotifier]  = None,
        search:    Optional[ITaskSearch]    = None,
        validator: Optional[ITaskValidator] = None,
    ) -> None:
        self._storage   = storage   or InMemoryTaskRepository()
        self._exporter  = exporter  or JsonExporter()
        self._notifier  = notifier  or ConsoleNotifier()
        self._search    = search    or TaskSearch()
        self._validator = validator or TaskValidator()
```

**Key design decisions:**

- All parameters are typed as interfaces, not concrete classes.
  `TaskManager` is decoupled from every implementation detail.
- Sensible defaults allow zero-argument construction for convenience and tests.
- No dependency-injection framework is needed — plain constructor arguments
  ("poor-man's DI") are sufficient and avoid adding external dependencies.

---

## 4. Swapping Implementations — Concrete Examples

All four combinations below use **identical `TaskManager` code**.
Only the injected objects differ.

```python
# Default — in-memory storage, JSON output, console notifications
tm = TaskManager()

# File-backed storage + CSV reports
tm = TaskManager(
    storage  = FileTaskRepository("prod_tasks.json"),
    exporter = CsvExporter(),
)

# File-backed storage + log-file notifications
tm = TaskManager(
    storage  = FileTaskRepository("prod_tasks.json"),
    notifier = LogFileNotifier("notifications.log"),
)

# Test double — capture notifications without stdout noise
messages = []
tm = TaskManager(
    storage  = InMemoryTaskRepository(),
    notifier = ConsoleNotifier(output_sink=messages.append),
)
```

---

## 5. How Interfaces Enable Low Coupling

### Dependency inversion

Before interfaces, `TaskManager` depended directly on `TaskRepository`
(a concrete class). Any change to that class could ripple into
`TaskManager`. After interfaces, `TaskManager` depends only on
`ITaskStorage` — an abstraction that never changes even as implementations
evolve.

```
Before (tight coupling):
  TaskManager  ──── imports ────►  TaskRepository  ──► dict

After (loose coupling):
  TaskManager  ──── depends on ──►  ITaskStorage   (abstract)
                                         ▲
                              ┌──────────┴──────────┐
                    InMemoryTaskRepository    FileTaskRepository
```

### Open/Closed Principle

Adding a new storage backend (e.g. `SqliteTaskRepository`) requires:
- Creating one new file that satisfies `ITaskStorage`
- Passing it to `TaskManager` at construction

`TaskManager`, `interfaces.py`, and all existing implementations remain
**unchanged**.

### Independent testability

Each interface can be substituted with a minimal stub in unit tests:

```python
class StubStorage:
    """Minimal ITaskStorage stub for unit tests."""
    def __init__(self): self._tasks = {}
    def add(self, task): self._tasks[task.task_id] = task; return task
    def get(self, task_id): return self._tasks[task_id]
    def update(self, task_id, updates): return self._tasks[task_id]
    def delete(self, task_id): del self._tasks[task_id]
    def list_all(self): return list(self._tasks.values())
    def assign(self, task_id, user_id): return self._tasks[task_id]
    def count(self): return len(self._tasks)

tm = TaskManager(storage=StubStorage())
```

Because `StubStorage` satisfies `ITaskStorage` structurally, no inheritance
or registration is needed.

### Runtime conformance verification

Because all Protocols use `@runtime_checkable`, conformance can be asserted:

```python
from interfaces import ITaskStorage
from components import InMemoryTaskRepository, FileTaskRepository

assert isinstance(InMemoryTaskRepository(), ITaskStorage)  # True
assert isinstance(FileTaskRepository("x.json"), ITaskStorage)  # True
```

The demo (`python task_manager.py`) performs this check for all six
implementations and prints a pass/fail table.

---

## 6. Interface Summary Table

| Interface | Method count | Implementations | Swappable without changing… |
|-----------|:------------:|-----------------|------------------------------|
| `ITaskStorage` | 7 | `InMemoryTaskRepository`, `FileTaskRepository` | `TaskManager`, all other components |
| `ITaskExporter` | 2 + 1 property | `JsonExporter`, `CsvExporter` | `TaskManager`, storage, notifier |
| `ITaskNotifier` | 2 | `ConsoleNotifier`, `LogFileNotifier` | `TaskManager`, storage, exporter |
| `ITaskSearch` | 3 | `TaskSearch` (+ future impls) | `TaskManager`, storage, exporter, notifier |
| `ITaskValidator` | 2 | `TaskValidator` (+ future impls) | `TaskManager`, storage, exporter, notifier |
