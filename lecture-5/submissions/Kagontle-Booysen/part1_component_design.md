# Part 1: Component Design — Task Management System

## 1. Overview

The Task Management System is decomposed into **five single-responsibility components** coordinated by a thin `TaskManager` orchestrator. Each component owns exactly one concern and exposes a minimal, injection-friendly interface.

```
code/
├── task_manager.py          # Orchestrator (wires components together)
├── models.py                # Pure data structures: Task, User, enums
└── components/
    ├── __init__.py
    ├── validator.py         # Input validation
    ├── repository.py        # Persistence (CRUD)
    ├── search.py            # Filtering & search
    ├── exporter.py          # JSON / CSV export
    └── notifier.py          # Reminder notifications
```

---

## 2. Component Decomposition

### 2.1 Models (`models.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Define shared data structures used across the system |
| **Key types** | `Task`, `User`, `Priority` (enum), `Status` (enum) |
| **Interface** | Data classes with `.to_dict()` serialisation helper |
| **Dependencies** | None — stdlib only (`dataclasses`, `datetime`, `enum`) |

**Rationale:** Centralising data structures in one place means every component speaks the same language. Keeping them free of business logic (no validation, no DB calls) prevents coupling and lets each structure be imported anywhere without pulling in side effects.

---

### 2.2 TaskValidator (`components/validator.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Validate raw input dictionaries *before* they touch the system |
| **Key methods** | `validate_new(data)`, `validate_update(data)` |
| **Interface** | Raises `ValidationError(field, message)` on failure |
| **Dependencies** | None — stdlib only |

**Rationale (SRP):** Validation rules change independently of persistence or business rules. Isolating them here means you can update allowed statuses, add new constraints, or swap validation libraries without touching the repository or orchestrator. The validator is also trivially unit-testable: pass a dict, expect either success or a `ValidationError`.

**Design decisions:**
- `validate_update()` only checks fields that are *present* in the payload, enabling safe partial updates.
- `ValidationError` carries a `field` attribute so callers can surface precise error messages to users.

---

### 2.3 TaskRepository (`components/repository.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Persist and retrieve `Task` objects |
| **Key methods** | `add()`, `get()`, `update()`, `delete()`, `list_all()`, `assign()` |
| **Interface** | Returns `Task` instances; raises `TaskNotFoundError` on missing IDs |
| **Dependencies** | `models.py` only |

**Rationale (SRP):** All storage concerns are co-located here. The current implementation uses an in-memory `dict`; swapping to SQLAlchemy, Redis, or any other backend requires changing *only this file* — callers remain unaffected because they program to the same interface (`add / get / update / delete`).

**Design decisions:**
- `update()` accepts a plain `dict` of partial fields, delegating any type coercion (e.g. `Priority(v)`) to this layer rather than the orchestrator.
- `assign()` is a semantic shortcut that delegates to `update()`, communicating intent clearly at the call site.

---

### 2.4 TaskSearch (`components/search.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Filter and sort a list of `Task` objects |
| **Key methods** | `filter(tasks, **criteria)`, `search(tasks, keyword)`, `sort(tasks, by, descending)` |
| **Interface** | Pure functions — input list in, filtered list out |
| **Dependencies** | `models.py` only |

**Rationale (SRP):** Search and filter logic is isolated from persistence. `TaskSearch` never calls the repository directly — it operates on whatever list is handed to it. This separation means:
- You can test search logic with a hand-crafted list without any DB setup.
- You can reuse the same search logic on a subset of tasks (e.g. tasks for one project).

**Design decisions:**
- `filter()` uses keyword-only arguments so callers can omit any criterion without ambiguity.
- `None` criteria are silently ignored, enabling flexible "query builder" style calls.
- `sort()` handles `None` due dates gracefully (they sort last) to avoid runtime crashes.

---

### 2.5 TaskExporter (`components/exporter.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Serialise a task list to JSON or CSV |
| **Key methods** | `export(tasks, fmt, filepath)`, `to_string(tasks, fmt)` |
| **Interface** | Returns the output string or file path; raises `UnsupportedFormatError` |
| **Dependencies** | `models.py`, stdlib (`json`, `csv`, `io`) |

**Rationale (SRP):** Export format details (field ordering, CSV escaping, JSON indentation) are entirely self-contained. Adding XML or XLSX export means adding one private method here — no other component is modified.

**Design decisions:**
- `to_string()` decouples serialisation from I/O, enabling use in API responses or tests without touching the filesystem.
- CSV list fields (`tags`) are flattened to semicolon-separated strings, a safe choice that preserves round-trip parsability.

---

### 2.6 TaskNotifier (`components/notifier.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Emit reminder notifications for tasks that are overdue or due soon |
| **Key methods** | `send_reminders(tasks, window_hours)`, `send_assignment_notice(task, user_name)` |
| **Interface** | Accepts an `OutputSink` callable; returns list of emitted messages |
| **Dependencies** | `models.py` only |

**Rationale (SRP):** Notification logic — determining urgency, formatting messages, routing output — is fully isolated. Swapping console output for email, Slack, or a push notification service requires changing only the injected `OutputSink`, not any other component.

**Design decisions:**
- Constructor injection of `OutputSink` makes the notifier 100% testable without capturing `sys.stdout`.
- Overdue tasks and upcoming tasks produce distinct message prefixes (`OVERDUE` vs `UPCOMING`) so downstream log parsers can distinguish them.
- Tasks with status `done` or `cancelled` are silently skipped — no noise for completed work.

---

### 2.7 TaskManager Orchestrator (`task_manager.py`)

| Attribute | Value |
|-----------|-------|
| **Responsibility** | Wire components together and expose a unified API |
| **Pattern** | Façade + Dependency Injection |
| **Dependencies** | All five components + `models.py` |

**Rationale:** `TaskManager` is the only place that knows about all components. It calls each in the right order (validate → persist, search → export, etc.) but adds no domain logic of its own. Every component is injected through the constructor, so tests can replace any one component with a mock or stub without subclassing or monkey-patching.

---

## 3. Coupling and Cohesion Analysis

### Coupling (low by design)

```
TaskManager  ──▶  TaskValidator   (no shared state)
             ──▶  TaskRepository  (no shared state)
             ──▶  TaskSearch      (receives list, returns list)
             ──▶  TaskExporter    (receives list, returns string/file)
             ──▶  TaskNotifier    (receives list, emits messages)

Components   ──▶  models.py       (shared data types only)
             ✗    each other      (zero cross-component imports)
```

No component imports another component. The only shared dependency is `models.py`, which is intentional — it is pure data with no logic that could create hidden coupling.

### Cohesion (high by design)

Every method inside each component serves its single stated responsibility. For example, `TaskSearch` contains *only* filtering/sorting methods; there is no temptation to add a `save()` method because persistence has its own dedicated component.

---

## 4. Extensibility Examples

| Change | Files modified |
|--------|----------------|
| Add PostgreSQL persistence | `repository.py` only |
| Add XML export format | `exporter.py` only (one new private method) |
| Send Slack notifications | `notifier.py` only (swap `OutputSink`) |
| Add a new validation rule | `validator.py` only |
| Add full-text search index | `search.py` only |
| All of the above | `task_manager.py` unchanged |

---

## 5. Dependency Injection Pattern

All components default-construct their dependencies if none are provided, but accept injected alternatives:

```python
# Production — defaults wired automatically
tm = TaskManager()

# Test — inject mocks / stubs
tm = TaskManager(
    repository = InMemoryTestRepository(),
    notifier   = CapturingNotifier(),     # captures messages for assertions
)
```

This pattern — sometimes called "poor-man's DI" — requires no framework while preserving full testability and loose coupling.
