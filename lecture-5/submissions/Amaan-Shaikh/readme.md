# Assignment Submission: Lecture 5

**Student Name**: Amaan Shaikh
**Submission Date**: 13.03.2026

## Overview

This submission contains a modular Task Management System implemented in Python, along with component design documentation and architecture analysis. The system demonstrates key software architecture concepts including modularity, separation of concerns, interfaces, dependency injection, and low coupling.

## Files Included

### Code Files
- `orchestrator.py` — Main class (TaskOrchestrator) coordinating the system workflow
- `task_models.py` — Data model definitions (TaskItem, enums)
- `demo.py` — Demonstration script showing how the system works with different implementations

### Component Files (`components/` folder)
- `verifier.py` — InputVerifier component for task data validation
- `storage.py` — IItemStore interface and implementations (Memory, JSON, SQLite)
- `finder.py` — ItemFinder component for searching and filtering tasks
- `formatter.py` — IItemFormatter interface and implementations (JSON, CSV, YAML, Markdown)
- `alerter.py` — TaskAlerter component for sending reminders

### Documentation Files
- `part1_component_design.md` — Component decomposition and design explanation
- `part1_interfaces.md` — Interfaces and dependency injection explanation
- `part2_component_diagram.drawio` — Component diagram (draw.io diagram)
- `part2_component_diagram.png` — Component diagram (image)
- `part2_cohesion_coupling.md` — Cohesion, coupling, and SRP analysis
- `README.md` — This file

## Key Highlights

- **Modular architecture** with 11 clearly separated components
- **Two interfaces** (IItemStore and IItemFormatter) enabling loose coupling
- **Multiple implementations** per interface:
  - Storage: Memory, JSON file, SQLite database
  - Formatter: JSON, CSV, YAML, Markdown
- **Dependency injection** used in TaskOrchestrator constructor
- **High cohesion** – each component has a single, focused responsibility
- **Low coupling** achieved through interfaces and dependency injection
- **Component diagram** aligned with the implemented architecture
- **Demonstration** of swapping implementations without changing the main class

## How to View and Run

1. **Diagrams**: Open `.drawio` files in [draw.io](https://app.diagrams.net/) to see editable diagrams
2. **Images**: View `.png` files for quick reference
3. **Documentation**: Read `.md` files in any text editor
4. **Run the code**:
   ```bash
   cd code
   python demo.py