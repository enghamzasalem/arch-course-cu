# Assignment Submission: Lecture 5

**Student Name**: Shreyash Ahir  
**Submission Date**: 2026-05-22

## Overview

Task Management System demonstrating modularity, component interfaces, dependency injection, and separation of concerns.

## How to Run

```bash
python main.py
```

No external dependencies. Python 3.8+ only.

## Files Included

```
shreyash-ahir/
├── main.py                          # Runnable demo (all features shown)
├── models.py                        # Data containers (Task, User, enums)
├── interfaces.py                    # ITaskStorage, ITaskExporter protocols
├── task_manager.py                  # Orchestrator — receives all deps via constructor
├── components/
│   ├── validator.py                 # TaskValidator
│   ├── repository.py                # InMemoryTaskRepository, FileTaskRepository
│   ├── search.py                    # TaskSearch
│   ├── exporter.py                  # JsonExporter, CsvExporter
│   └── notifier.py                  # TaskNotifier
├── part1_component_design.md        # Component decomposition + rationale
├── part1_interfaces.md              # Interfaces + dependency injection analysis
├── part2_component_diagram.drawio   # draw.io source diagram
├── part2_component_diagram.png      # Exported PNG
└── part2_cohesion_coupling.md       # Cohesion, coupling, SRP analysis
```

## Key Highlights

- **Two interfaces** (`ITaskStorage`, `ITaskExporter`) enable swapping storage and export implementations without modifying `TaskManager`
- **Constructor injection** — `TaskManager` never instantiates its dependencies
- **Pure data model** — `models.py` has no behaviour; all components depend on it as cheap data coupling only
- **No external libraries** — stdlib only (`json`, `csv`, `dataclasses`, `typing`)

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams
2. View `.png` files for quick reference
3. Read `.md` files for documentation
4. Run `python main.py` for a live demo of all features
