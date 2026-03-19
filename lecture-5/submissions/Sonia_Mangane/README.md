# Assignment Submission: Lecture 5 - Modular Component Design

**Student Name**: Sonia Mangane  

**Submission Date**: 10 March 2026

---

## Overview

This assignment implements a **Modular Task Management System**. The  focus is on **Separation of Concerns (SoC)** and **Dependency Inversion**. By decomposing the system into components that communicate through formal Python `Protocols`, I have created a system where implementations (like storage or exporting) can be swapped without modifying the core business logic.

---

## Files Included

### 1. Core Implementation (`code/`)
* **`task_manager.py`**: The central Orchestrator. It remains "implementation-agnostic" by utilizing Dependency Injection.
* **`models.py`**: Contains the `Task` dataclass and `TaskPriority` Enums.
* **`main.py`**: The entry point that demonstrates the system's flexibility by swapping between Memory/JSON and File/CSV scenarios.

### 2. Modular Components (`code/components/`)
* **`validator.py`**: Encapsulates business rule validation logic.
* **`repository.py`**: Manages persistence via `ITaskStorage` (In-Memory and File implementations).
* **`exporter.py`**: Transforms data via `ITaskExporter` (JSON and CSV implementations).
* **`notifier.py`**: Handles simulated user notifications.
* **`search.py`**: Provides specialized filtering and search capabilities.
* **`logger.py`**: Implements a cross-cutting logging concern to track system events.

### 3. Documentation & Diagrams
* **`part1_component_design.md`**: Analysis of component responsibilities and rationale.
* **`part1_interfaces.md`**: Documentation of Protocols and the Dependency Injection pattern.
* **`part2_cohesion_coupling.md`**: In-depth analysis of coupling levels and cohesion types.
* **`part2_component_diagram.drawio` / `.png`**: Visual representation of the modular architecture.

---

## Key Highlights

* **Low Coupling via Dependency Injection**: The `TaskManager` never instantiates its own dependencies. By injecting them via the constructor, the system achieves a "plug-and-play" architecture.
    
* **Handling Complex Serialization**: The `Exporter` and `Repository` components include custom "data cleaning" logic to safely serialize `Enum` and `datetime` objects into JSON-compatible formats.
* **Cross-Cutting Concerns**: By adding the `TaskLogger`, the system demonstrates **Observability** without cluttering the business logic with print statements.
    

---

## How to View & Run

### Prerequisites
* Python 3.8+ 

### Execution
To run the demonstration script and see the modularity in action:
```bash
cd submissions/Sonia_Mangane/code
python3 main.py