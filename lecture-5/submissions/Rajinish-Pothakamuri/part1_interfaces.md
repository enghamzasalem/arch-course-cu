# Part 1.2: Interfaces and Dependency Injection

## 1. Overview

To achieve low coupling and modularity, the Task Management System uses **interfaces and dependency injection**.
Interfaces define the expected behavior of components, while dependency injection allows implementations to be swapped without modifying the core system.

This design follows the **Dependency Inversion Principle**, where high-level modules depend on abstractions rather than concrete implementations.

---

# 2. Interfaces

The system defines several interfaces using Python's `Protocol` type.

Interfaces specify the required methods without defining implementation details.

---

## 2.1 ITaskRepository

**Location:** `components/repository.py`

**Purpose**

Defines the interface for task storage operations.

```
class ITaskRepository(Protocol):
    def add(self, task: Task) -> None: ...
    def update(self, task: Task) -> None: ...
    def delete(self, task_id: str) -> None: ...
    def get(self, task_id: str) -> Optional[Task]: ...
    def list_all(self) -> List[Task]: ...
```

### Implementations

Two implementations are provided:

**InMemoryTaskRepository**

* Stores tasks in memory using a dictionary
* Useful for testing and temporary storage

**FileTaskRepository**

* Stores tasks in a JSON file
* Provides persistent storage

These implementations follow the same interface and can be swapped easily.

---

## 2.2 ITaskExporter

**Location:** `components/exporter.py`

**Purpose**

Defines the interface for exporting tasks to external formats.

```
class ITaskExporter(Protocol):
    def export(self, tasks: List[Task]) -> str: ...
```

### Implementations

Two exporters implement this interface:

**JsonTaskExporter**

* Converts tasks to JSON format

**CsvTaskExporter**

* Converts tasks to CSV format

Both exporters implement the same method `export()`.

---

## 2.3 ITaskNotifier

**Location:** `components/notifier.py`

**Purpose**

Defines the interface for sending task reminders.

```
class ITaskNotifier(Protocol):
    def send_reminder(self, task: Task, message: str) -> None: ...
```

### Implementations

**ConsoleTaskNotifier**

* Prints reminder messages to the console

**SilentTaskNotifier**

* Performs no action
* Useful for testing environments

---

## 2.4 ITaskValidator

**Location:** `components/validator.py`

**Purpose**

Defines the interface for validating task data before creation or update.
```
class ITaskValidator(Protocol):
    def validate_new(self, task: Task) -> Tuple[bool, List[str]]: ...
    def validate_update(self, task: Task) -> Tuple[bool, List[str]]: ...
```

### Implementations

**TaskValidator**

* Validates that task ID and title are present
* Enforces minimum title length of 3 characters
* Used for both creation and update validation

---

# 3. Dependency Injection

The main orchestrator (`TaskManager`) receives dependencies through its constructor.

```
class TaskManager:

    def __init__(
        self,
        validator: ITaskValidator,
        repository: ITaskRepository,
        search: TaskSearch,
        exporters: Dict[str, ITaskExporter],
        notifier: ITaskNotifier,
    )
```

This means the `TaskManager` does not create components itself.
Instead, the required implementations are provided when the object is created.

Example:

```
TaskManager(
    validator=ITaskValidator(),
    repository=InMemoryTaskRepository(),
    search=TaskSearch(repo),
    exporters={
        "json": JsonTaskExporter(),
        "csv": CsvTaskExporter()
    },
    notifier=ConsoleTaskNotifier()
)
```

---

# 4. Swapping Implementations

Because the system depends on interfaces, implementations can be replaced without modifying `TaskManager`.

Example 1: In-memory storage

```
repo = InMemoryTaskRepository()
```

Example 2: File storage

```
repo = FileTaskRepository("data/tasks.json")
```

Both implementations work without changing the `TaskManager` code.

---

# 5. Benefits of Using Interfaces

Using interfaces provides several advantages:

### Low Coupling

Components depend on abstractions instead of concrete implementations.

### Flexibility

New implementations can be added easily (e.g., database repository, XML exporter).

### Testability

Mock or dummy implementations can be used for testing.

### Maintainability

Changes to one component do not affect others.

---

# 6. Conclusion

The Task Management System uses interfaces and dependency injection to achieve a modular and loosely coupled architecture.

Key interfaces include:

* `ITaskValidator`
* `ITaskRepository`
* `ITaskExporter`
* `ITaskNotifier`

Each interface has multiple implementations, allowing the system to swap components easily while keeping the `TaskManager` unchanged.
