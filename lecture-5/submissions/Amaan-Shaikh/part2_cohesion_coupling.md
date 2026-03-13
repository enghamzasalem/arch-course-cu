# Task 2.2 – Cohesion and Coupling Analysis

**Student Name**: Amaan Shaikh
**Submission Date**: 13.03.2026

## A) Cohesion Analysis

### TaskOrchestrator
Cohesion type: Sequential cohesion  

TaskOrchestrator coordinates the workflow of the application. It calls the verifier, finder, storage, formatter, and alerter in sequence to complete operations.  
It has high cohesion because all of its methods are related to managing the overall task workflow from creation to export.

### InputVerifier
Cohesion type: Functional cohesion  

InputVerifier is responsible only for validating task data. It checks fields such as title and deadline, and validates status and priority during updates. All logic inside this component is related to validation, so it has high cohesion.

### ItemFinder
Cohesion type: Functional cohesion  

ItemFinder handles searching and filtering tasks. It supports text search and filtering by owner, status, priority, and labels.  
All methods focus on finding subsets of tasks, which gives it high cohesion.

### TaskAlerter
Cohesion type: Functional cohesion  

TaskAlerter sends reminder messages for upcoming deadlines.  
Its only responsibility is notifications, so the component is highly cohesive.

### Storage Components
Cohesion type: Functional cohesion  

**MemoryItemStore**, **JsonItemStore**, and **SqliteItemStore** manage storing and retrieving tasks.  
All methods in these classes are related to CRUD operations (add, get, update, delete), which gives them strong cohesion.

### Formatter Components
Cohesion type: Functional cohesion  

**JsonFormatter**, **CsvFormatter**, **YamlFormatter**, and **MarkdownFormatter** are responsible for exporting tasks to different formats.  
Each formatter focuses only on converting tasks to a specific format, which results in high cohesion.

---

## B) Coupling Analysis

### TaskOrchestrator and other components
Coupling level: Low to Medium  

TaskOrchestrator coordinates other components but does not implement their logic.  
Validation, searching, storage, formatting, and notifications are delegated to separate components, which keeps dependencies manageable.

### TaskOrchestrator and IItemStore
Coupling level: Low  

TaskOrchestrator depends on the **IItemStore** interface instead of a specific storage implementation.  
This allows switching between **MemoryItemStore**, **JsonItemStore**, and **SqliteItemStore** without changing TaskOrchestrator.

### TaskOrchestrator and IItemFormatter
Coupling level: Low  

TaskOrchestrator uses the **IItemFormatter** interface.  
This makes it possible to change the export format (JSON, CSV, YAML, Markdown) without modifying the orchestrator.

### TaskOrchestrator and concrete components
Coupling level: Medium  

TaskOrchestrator currently depends directly on **InputVerifier**, **ItemFinder**, and **TaskAlerter** concrete classes.  
While these dependencies are stable, they create tighter coupling than necessary.

### How low coupling was achieved
- **Interfaces** for storage (IItemStore) and formatting (IItemFormatter)
- **Dependency injection** in the TaskOrchestrator constructor
- **No shared global state** between components
- **Single responsibility** keeping components focused

### Possible improvements
If more time was available, interfaces could also be added for:

- **InputVerifier** – create IVerifier interface
- **ItemFinder** – create IFinder interface
- **TaskAlerter** – create IAlerter interface

This would reduce coupling even further and make the architecture more consistent. TaskOrchestrator would then depend only on interfaces, achieving 100% low coupling.

---

## C) SRP Application

### TaskOrchestrator
Responsibility: Coordinate the task management workflow.  
Reason to change: If the overall workflow or business process changes.

### InputVerifier
Responsibility: Validate task input data.  
Reason to change: If validation rules change (e.g., title length, date format).

### ItemFinder
Responsibility: Search and filter tasks.  
Reason to change: If search logic changes (e.g., add fuzzy search, new filter criteria).

### TaskAlerter
Responsibility: Send reminder notifications.  
Reason to change: If the notification mechanism changes (e.g., email instead of console).

### Storage classes (MemoryItemStore, JsonItemStore, SqliteItemStore)
Responsibility: Store and retrieve tasks.  
Reason to change: If the storage method or schema changes.

### Formatter classes (JsonFormatter, CsvFormatter, YamlFormatter, MarkdownFormatter)
Responsibility: Export tasks to a specific format.  
Reason to change: If the export format structure changes.

---

## Diagram
![Component Diagram](part2_component_diagram.png)