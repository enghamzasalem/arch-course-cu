# Task 1.1 - Component Design

## Component Decomposition

The system is divided into the following components:

### TaskManager
The TaskManager is the central class that coordinates the system.

Responsibilities:
- handles user actions
- connects other components together
- manages the overall workflow

It does not implement storage or validation logic itself. Instead, it delegates those tasks to other components.

---

### TaskValidator
The TaskValidator checks whether task input data is valid before it is processed.

Responsibilities:
- validate new tasks
- validate updates

Examples of checks:
- task id must exist
- title should not be empty
- status and priority values must be valid during updates

Separating validation makes the system easier to maintain if validation rules change later.

---

### TaskRepository
The repository is responsible for storing and retrieving tasks.

Responsibilities:
- add tasks
- get tasks
- update tasks
- delete tasks

Two implementations are used:

- **InMemoryTaskRepository** – stores tasks in memory
- **FileTaskRepository** – stores tasks in a JSON file

This allows switching the storage method without changing the TaskManager.

---

### TaskSearch
The TaskSearch component is responsible for searching and filtering tasks.

Responsibilities:
- keyword search
- filtering by status
- filtering by priority
- filtering by assignee

Separating search logic keeps the repository simpler.

---

### TaskExporter
This component exports task data to external formats.

Responsibilities:
- export tasks to JSON
- export tasks to CSV

Two implementations are provided:
- JsonExporter
- CsvExporter

This demonstrates how different implementations can be used without changing the main system.

---

### TaskNotifier
The TaskNotifier simulates task reminders.

Responsibilities:
- print reminder messages for tasks

In a real system this could send emails or notifications.

---

## Design Rationale

The main design goal was modularity.  
Each component has a single responsibility and focuses on one type of task.

This makes the system:

- easier to understand
- easier to modify
- easier to test

---

## Component Interaction

The components interact in the following way:

1. The user interacts with the **TaskManager**
2. The **TaskValidator** checks the input
3. The **TaskRepository** stores or retrieves data
4. The **TaskSearch** handles searching and filtering
5. The **TaskExporter** exports task data
6. The **TaskNotifier** sends reminder messages

The TaskManager acts as the main coordinator while the other components handle specific responsibilities.