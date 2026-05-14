# Part 1.2: Interfaces and Dependency Injection Analysis

## Interfaces (Protocols)
Reduced coupling is achieved by using Python `Protocol` to define component contracts. This ensures that the orchestrator depends only on behavior, not specific implementations. The interfaces are defined in `code/interfaces.py`:

### 1. ITaskStorage
- **Purpose**: Defines methods for task persistence (`add`, `get_all`, `find_by_id`).
- **Implementations** (in `repository.py`):
  - `InMemoryTaskRepository`: An in-memory implementation.
  - `FileTaskRepository`: A file-based implementation.

### 2. ITaskExporter
- **Purpose**: Defines the `export` method for converting task data.
- **Implementations** (in `exporter.py`):
  - `JsonExporter`: A JSON-based implementation.
  - `CsvExporter`: A CSV-based implementation.

## Dependency Injection (DI)
The `TaskManager` class receives its dependencies through its constructor. This allows for:
- **Zero-Change Swapping**: Switching from Memory to File storage or JSON to CSV export without modifying the `TaskManager` class.
- **Improved Testability**: Components can be easily replaced with mocks for isolated testing.
- **Adherence to DIP**: High-level modules (`TaskManager`) no longer depend on low-level modules, but both depend on abstractions.

## Demonstration
The `main.py` script demonstrates two distinct configurations of the same `TaskManager`, proving that it functions correctly regardless of which specific implementation is injected.
