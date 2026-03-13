# Task 1.2 – Interfaces and Dependency Injection

## Interfaces Used

In the system, I defined two interfaces:

- IItemStore
- IItemFormatter

These interfaces were created using Protocol.

---

## IItemStore

The IItemStore interface defines the basic operations for storing and managing tasks.

Methods included:

- add_item(item)
- get_item(item_id)
- get_all_items()
- update_item(item)
- remove_item(item_id)

### Implementations

Three repository implementations were created:

1. **MemoryItemStore**  
   This version stores tasks in a Python dictionary.  
   It is simple and useful for testing or small examples.

2. **JsonItemStore**  
   This version stores tasks in a JSON file.  
   It allows data to stay available after the program stops.

3. **SqliteItemStore**  
   This version stores tasks in a SQLite database.  
   It provides more robust storage for larger applications.

Because all classes follow the same interface, they can be swapped without changing the TaskOrchestrator.

---

## IItemFormatter

The IItemFormatter interface defines how task data is exported.

Method included:

- format_items(tasks)

### Implementations

Four formatter implementations were created:

1. **JsonFormatter**  
   Exports task data in JSON format.

2. **CsvFormatter**  
   Exports task data in CSV format.

3. **YamlFormatter**  
   Exports task data in YAML format.

4. **MarkdownFormatter**  
   Exports task data as a Markdown table.

This makes the system more flexible because the export format can be changed easily.

---

## Dependency Injection

Dependency injection was used in the TaskOrchestrator constructor.

The TaskOrchestrator receives its dependencies from outside instead of creating them inside the class.

Example:
```python
orchestrator = TaskOrchestrator(
    storage=MemoryItemStore(),
    verifier=InputVerifier(),
    finder=ItemFinder(),
    formatter=JsonFormatter(),
    alerter=TaskAlerter()
)
```

## Swapping Implementations

One advantage of this approach is that implementations can be changed without modifying the TaskOrchestrator.

For example, the storage and formatter can be swapped like this:

```python
# Using JSON file storage with CSV exporter
orchestrator = TaskOrchestrator(
    storage=JsonItemStore("tasks.json"),
    verifier=InputVerifier(),
    finder=ItemFinder(),
    formatter=CsvFormatter(),
    alerter=TaskAlerter()
)

# Or using SQLite storage with Markdown exporter
orchestrator = TaskOrchestrator(
    storage=SqliteItemStore("tasks.db"),
    verifier=InputVerifier(),
    finder=ItemFinder(),
    formatter=MarkdownFormatter(),
    alerter=TaskAlerter()
)
```
The TaskOrchestrator works the same way regardless of which implementations are used, demonstrating low coupling and flexibility.