# Part 1.1: Component Decomposition Analysis

## Overview
The Task Management System has been decomposed into modular components, each following the Single Responsibility Principle (SRP). This design ensures that each part of the system has one clear reason to change and promotes low coupling and high cohesion.

## Identified Components

### 1. TaskValidator
- **Responsibility**: Validates task data to ensure integrity (e.g., checking for required fields).
- **Rationale**: Separating validation logic prevents other components from having to know about specific validation rules.

### 2. TaskRepository
- **Responsibility**: Manages the persistence and retrieval of task entities.
- **Rationale**: Encapsulating storage logic allows for swapping the storage mechanism (e.g., from in-memory to a database) without affecting the rest of the system.

### 3. TaskSearch
- **Responsibility**: Provides filtering and searching capabilities across the task collection.
- **Rationale**: Search logic can become complex; keeping it separate ensures that the repository remains focused on basic CRUD operations.

### 4. TaskExporter
- **Responsibility**: Handles the conversion of task data into external formats (like JSON or CSV).
- **Rationale**: Export logic is distinct from core task management and may involve external libraries or specific formatting rules.

### 5. TaskNotifier
- **Responsibility**: Manages communication with users regarding task status or reminders.
- **Rationale**: Decouples the notification medium (console, email, SMS) from the core business logic of managing tasks.

## Modular Structure
The code is organized into a `code/` directory with a `components/` subdirectory:
- `code/main.py`: Demo entry point.
- `code/task_manager.py`: Orchestrator that coordinates component interactions.
- `code/models.py`: shared data structures (Task, etc.).
- `code/components/`: Directory containing the individual component implementations.
