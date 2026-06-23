## Part 1.2: Interfaces and Dependency Injection

### 1. Interface Definitions

In this project, I used Python **Protocols (`typing.Protocol`)** to define interfaces.  
This allows the system to follow **structural typing**, meaning that different classes can be used as long as they implement the required methods.  
Because of this, the `TaskManager` does not depend on specific implementations.

---

### ITaskRepository (Persistence Interface)

**Responsibility:**  
The `ITaskRepository` interface defines how tasks are stored and retrieved in the system.

**Key Methods:**

- `add(task: Task)`
- `get_all() -> List[Task]`

**Why it improves modularity:**  
The system does not depend on how the tasks are stored. For example, we can use `InMemoryTaskRepository` during development or testing, and later switch to `FileTaskRepository` for permanent storage without changing the `TaskManager`.

---

### ITaskExporter (Export Interface)

**Responsibility:**  
The `ITaskExporter` interface defines how tasks are exported into external formats.

**Key Methods:**

- `export(tasks: List[Task], path: str)`

**Why it improves modularity:**  
This interface separates the exporting logic from the rest of the system. It handles file formatting and serialization so that the `TaskManager` does not need to know how JSON or CSV files are created.

---

## 2. Dependency Injection (DI) Implementation

The `TaskManager` does not create its own dependencies.  
Instead, the required components are passed into the constructor. This approach is called **Dependency Injection**.

Example:

    class TaskManager:
        def __init__(self, repository: ITaskRepository, exporter: ITaskExporter):
            # Dependencies are injected into the manager
            self.repository = repository
            self.exporter = exporter

By injecting dependencies, the `TaskManager` focuses only on managing tasks, while other components handle storage and exporting.

---

## 3. Benefits of This Design

### Low Coupling

The `TaskManager` depends on **interfaces** (`ITaskRepository`, `ITaskExporter`) instead of specific classes.  
This reduces coupling because the main logic does not rely on a particular implementation.

For example, if the storage method changes from file-based storage to a database, a new repository implementation can be created without modifying the `TaskManager`.

---

### High Cohesion

Each component in the system has a single responsibility:

- **TaskExporter** is responsible for exporting tasks to files.
- **TaskRepository** is responsible for storing and retrieving tasks.
- **TaskManager** is responsible for coordinating task operations.

This makes the system easier to understand and maintain.

---

### Swappability Demonstration

The system allows different implementations to be swapped easily.

Examples demonstrated in `main.py`:

- **Scenario A:** `InMemoryTaskRepository` with `JsonExporter`
- **Scenario B:** `FileTaskRepository` with `CsvExporter`

Because the system uses interfaces and dependency injection, these components can be replaced without changing the core task management logic.