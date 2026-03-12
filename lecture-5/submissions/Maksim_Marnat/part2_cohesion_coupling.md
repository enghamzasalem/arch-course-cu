# Part 2.2 – Cohesion and Coupling Analysis

## a) Cohesion Analysis

- **TaskManager**: Functional. All methods coordinate task use cases (create, update, search, export, reminders). Search and reminder logic are in TaskManager for a minimal submission.
- **TaskValidator**: Functional. Only validation rules; one reason to change when rules change.
- **InMemoryTaskRepository / FileTaskRepository**: Functional. Only store and retrieve tasks.
- **JsonTaskExporter / CsvTaskExporter**: Functional. Only convert tasks to one output format each.

## b) Coupling Analysis

- **TaskManager → ITaskStorage, ITaskExporter, TaskValidator**: Low coupling via constructor injection; TaskManager depends on interfaces (Protocols), not concrete classes.
- **Repositories and exporters** depend only on `Task` and do not depend on each other.
- **How low coupling was achieved**: Two interfaces (ITaskStorage, ITaskExporter), constructor injection in TaskManager, wiring in `main.py` so implementations can be swapped.

## c) SRP Application

- **TaskManager**: One reason to change—orchestration flow.
- **TaskValidator**: Validation rules.
- **Repositories**: Storage mechanism.
- **Exporters**: Output format.

![Component Diagram](part2_component_diagram.png)
