# Part 1 — Interfaces and Dependency Injection

## The Two Interfaces

Both interfaces are defined in `interfaces.py` using Python's
`typing.Protocol` with `@runtime_checkable`.  Protocol-based interfaces
work through structural typing: any class that provides the right methods
satisfies the contract, with no inheritance required.

---

### ITaskStorage

```python
class ITaskStorage(Protocol):
    def save(self, task: Task) -> None: ...
    def get(self, task_id: str) -> Optional[Task]: ...
    def delete(self, task_id: str) -> bool: ...
    def list_all(self) -> List[Task]: ...
```

**What it hides:** The storage medium.  Callers never know whether data
lives in RAM, on disk, in a database, or in a remote API.

**Concrete implementations:**

| Class | Where | Trade-off |
|---|---|---|
| `InMemoryTaskRepository` | `components/repository.py` | Fast, no I/O; data lost on process exit. Ideal for tests. |
| `FileTaskRepository` | `components/repository.py` | Persists to JSON on disk.  Survives restarts. |

---

### ITaskExporter

```python
class ITaskExporter(Protocol):
    def export(self, tasks: List[Task], destination: str) -> str: ...
```

**What it hides:** The output format and the I/O mechanism.

**Concrete implementations:**

| Class | Where | Output |
|---|---|---|
| `JsonExporter` | `components/exporter.py` | JSON file or JSON string |
| `CsvExporter`  | `components/exporter.py` | CSV file or CSV string  |

---

## How Dependency Injection Is Applied

`TaskManager` receives all dependencies through its constructor:

```python
class TaskManager:
    def __init__(
        self,
        storage: ITaskStorage,    # <-- interface, not a concrete class
        exporter: ITaskExporter,  # <-- interface, not a concrete class
        validator: Optional[TaskValidator] = None,
        searcher: Optional[TaskSearch] = None,
        notifier: Optional[TaskNotifier] = None,
    ) -> None:
```

`TaskManager` never imports `InMemoryTaskRepository`, `FileTaskRepository`,
`JsonExporter`, or `CsvExporter`.  The caller (`main.py`) decides which
implementations to use at startup.

This follows the **Hollywood Principle** ("don't call us, we'll call you"):
`TaskManager` does not go looking for its dependencies — they are pushed in
from outside.

---

## Demonstrating Swappability

From `main.py`:

```python
# Default: in-memory storage + JSON export
manager = TaskManager(
    storage=InMemoryTaskRepository(),
    exporter=JsonExporter(),
)

# Swap to file storage + CSV export — TaskManager code unchanged
manager2 = TaskManager(
    storage=FileTaskRepository("tasks.json"),
    exporter=CsvExporter(),
)
```

Both managers call `storage.save(...)` and `exporter.export(...)` exactly
the same way.  The interface is the stable contract; the implementation is
the replaceable detail.

---

## How the Interfaces Enable Low Coupling

Coupling is the degree to which a change in one component forces a change
in another.  The interfaces reduce coupling in three concrete ways:

**1. No import of concrete classes.**  
`TaskManager` imports only `ITaskStorage` and `ITaskExporter`.  Adding a
third storage backend (e.g., `DatabaseTaskRepository`) requires zero changes
to `TaskManager`.

**2. Independent testability.**  
Any test for `TaskManager` can inject a trivial stub that satisfies the
`ITaskStorage` protocol without needing a real file or database.  The
components can be tested in isolation with no shared state.

**3. Runtime substitution.**  
Because the binding happens in the constructor at startup, the system can be
reconfigured (e.g., different storage for test vs. production) without
recompiling or modifying any component — exactly the benefit described in
the course material on Dependency Injection.
