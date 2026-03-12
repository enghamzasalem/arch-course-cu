# Part 1 – Component Decomposition

## Overview

The Task Management System is designed using modular architecture principles. The system is decomposed into independent components, each responsible for a specific concern. This approach improves maintainability, testability, and extensibility.

The architecture follows the **Single Responsibility Principle (SRP)** and **Separation of Concerns**, ensuring that each component performs a clearly defined task.

---

# System Components

The system is divided into the following main components:

## 1. TaskManager

**Responsibility**

The TaskManager acts as the central orchestrator of the system. It coordinates interactions between the other components and exposes high-level operations for managing tasks.

**Key operations**

- Create tasks
- Update tasks
- Delete tasks
- List tasks
- Export tasks
- Send reminders

TaskManager does not implement business logic directly; instead, it delegates responsibilities to specialized components.

---

## 2. TaskValidator

**Responsibility**

The TaskValidator is responsible for validating task data before it is stored in the system.

Examples of validations include:

- Ensuring that the task title is not empty
- Ensuring the title meets minimum length requirements

By separating validation logic, the system maintains clear boundaries between validation and storage logic.

---

## 3. TaskRepository

**Responsibility**

The TaskRepository component handles the storage and retrieval of tasks.

Two implementations are provided:

- **InMemoryTaskRepository** – stores tasks in memory
- **FileTaskRepository** – stores tasks in a JSON file

This design allows the storage mechanism to be changed without modifying the TaskManager.

---

## 4. TaskSearch

**Responsibility**

The TaskSearch component provides filtering and search functionality for tasks.

Supported operations include:

- Searching tasks by status
- Searching tasks by assignee

Separating search logic keeps the repository focused only on data storage.

---

## 5. TaskExporter

**Responsibility**

The TaskExporter component is responsible for exporting tasks to external formats.

Two exporters are implemented:

- **JsonExporter**
- **CsvExporter**

This design allows new export formats to be added without modifying the existing system.

---

## 6. TaskNotifier

**Responsibility**

The TaskNotifier component is responsible for sending reminders for tasks.

In this assignment, reminders are simulated using console output.

---

# Design Rationale

The system is decomposed to ensure that each component has a **single responsibility**.

Benefits of this modular design include:

- Easier testing of individual components
- Clear separation of responsibilities
- Improved maintainability
- Ability to replace components without affecting the entire system

This architecture also supports extensibility. For example, new exporters or repositories can be added with minimal impact on existing components.