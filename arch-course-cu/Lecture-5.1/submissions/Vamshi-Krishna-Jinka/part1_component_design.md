# Task 1.1 – Component Decomposition

## Overview

The Task Management System was designed using modular architecture principles.
The system is decomposed into independent components, each following the
Single Responsibility Principle (SRP).

Each component performs one clearly defined task and communicates through
minimal interfaces.

---

## Components

### 1. TaskValidator

Responsibility:
Validate task data before it is stored.

Rationale:
Validation logic is separated from business logic to maintain SRP
and allow independent testing.

---

### 2. TaskRepository

Responsibility:
Store and retrieve tasks.

Rationale:
The repository isolates data storage from business logic.
This allows switching storage implementations without affecting
other components.

---

### 3. TaskSearch

Responsibility:
Filter and search tasks.

Rationale:
Search logic is separated from storage and business logic to
maintain modularity.

---

### 4. TaskExporter

Responsibility:
Export tasks to different formats (JSON and CSV).

Rationale:
Export functionality is isolated to support multiple formats
without modifying other parts of the system.

---

### 5. TaskNotifier

Responsibility:
Send reminders for tasks.

Rationale:
Notification logic is separated from task management logic,
making it easy to replace with email or push notifications later.

---

## Benefits of the Design

High Cohesion:
Each component performs one specific function.

Low Coupling:
Components interact through simple interfaces.

Testability:
Each component can be tested independently.

Maintainability:
Changes in one component do not affect others.