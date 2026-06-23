# Lecture 5 Assignment — Modular Task Management System (Maksim_Marnat)

Modular Task Management System in Python: components, interfaces, and dependency injection.

## Contents

| File | Description |
|------|-------------|
| `code/models.py` | Task model (`Task`, `TaskStatus`, `TaskPriority`) |
| `code/components/interfaces.py` | `ITaskStorage`, `ITaskExporter` (Protocol) |
| `code/components/validator.py` | `TaskValidator` |
| `code/components/repository.py` | `InMemoryTaskRepository`, `FileTaskRepository` |
| `code/components/exporter.py` | `JsonTaskExporter`, `CsvTaskExporter` |
| `code/task_manager.py` | `TaskManager` (orchestrator, DI) |
| `code/main.py` | Demo: two configs (in-memory+JSON, file+CSV) |
| `part1_component_design.md` | Component decomposition (Part 1.1) |
| `part1_interfaces.md` | Interfaces and DI (Part 1.2) |
| `part2_component_diagram.drawio` | Component diagram |
| `part2_cohesion_coupling.md` | Cohesion/coupling analysis (Part 2.2) |

## How to Run

```bash
cd lecture-5/submissions
python3 -m Maksim_Marnat.code.main
```

Output: creates tasks, updates status, exports to `tasks.json` and `tasks.csv`, prints a reminder. No external deps (stdlib only).

## Assignment Mapping

- **Part 1.1**: 5+ components (TaskManager, TaskValidator, 2 repos, 2 exporters); SRP; see `part1_component_design.md`.
- **Part 1.2**: 2 interfaces, 2 implementations each; TaskManager receives deps via constructor; swap shown in `main.py`; see `part1_interfaces.md`.
- **Part 2.1**: `part2_component_diagram.drawio`; export PNG in draw.io (File → Export as → PNG) for submission.
- **Part 2.2**: `part2_cohesion_coupling.md`.
