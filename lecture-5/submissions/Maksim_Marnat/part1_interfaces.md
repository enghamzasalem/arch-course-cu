# Part 1.2 – Interfaces and Dependency Injection

## Interfaces (`code/components/interfaces.py`)

### 1. ITaskStorage

- **Purpose**: Abstract task persistence.
- **Methods**: `add(task)`, `get(task_id)`, `list_all()`, `update(task)`, `delete(task_id)`, `find_by_assignee(assignee)`.
- **Implementations**: `InMemoryTaskRepository`, `FileTaskRepository`.
- **Benefit**: TaskManager depends on the interface; storage can be swapped without changing TaskManager.

### 2. ITaskExporter

- **Purpose**: Serialize tasks to a format (e.g. file).
- **Method**: `export(tasks, destination)`.
- **Implementations**: `JsonTaskExporter`, `CsvTaskExporter`.
- **Benefit**: Export format can be swapped without changing TaskManager.

## Dependency Injection

TaskManager receives dependencies via constructor:

```python
def __init__(self, storage: ITaskStorage, exporter: ITaskExporter, validator: Optional[TaskValidator] = None)
```

- **Low coupling**: TaskManager does not instantiate storage or exporter; they are injected.
- **Swapping**: `main.py` builds two configurations—in-memory + JSON, then file + CSV—without changing TaskManager code.
