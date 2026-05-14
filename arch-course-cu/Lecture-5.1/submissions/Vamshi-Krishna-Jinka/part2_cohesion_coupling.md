# Task 2.2 – Cohesion and Coupling Analysis

![Component Diagram](part2_component_diagram.png)

---

# a) Cohesion Analysis

Cohesion refers to how closely related the responsibilities of a component are.
The goal of the design is **high cohesion**, meaning each component focuses on a single well-defined responsibility.

### TaskManager

**Type of Cohesion:** Functional Cohesion

**Explanation:**
TaskManager orchestrates task-related operations such as creating tasks, deleting tasks, searching tasks, exporting tasks, and sending reminders. These operations are all directly related to managing tasks.

**Why it is Highly Cohesive:**
All methods inside this component are focused on coordinating task operations.

---

### TaskValidator

**Type of Cohesion:** Functional Cohesion

**Explanation:**
TaskValidator only performs validation of task data before tasks are stored.

**Why it is Highly Cohesive:**
Every method in this component contributes directly to validating task data.

---

### TaskRepository / InMemoryTaskRepository

**Type of Cohesion:** Functional Cohesion

**Explanation:**
This component manages task persistence operations such as storing, retrieving, and deleting tasks.

**Why it is Highly Cohesive:**
All methods are related to task storage and retrieval.

---

### TaskSearch

**Type of Cohesion:** Functional Cohesion

**Explanation:**
TaskSearch is responsible only for filtering and searching tasks.

**Why it is Highly Cohesive:**
All methods operate on searching or filtering tasks.

---

### TaskExporter (JsonExporter, CsvExporter)

**Type of Cohesion:** Functional Cohesion

**Explanation:**
Exporter components focus only on exporting task data to specific formats.

**Why it is Highly Cohesive:**
Each exporter is dedicated to one format and one function: exporting tasks.

---

### TaskNotifier

**Type of Cohesion:** Functional Cohesion

**Explanation:**
This component sends reminders for tasks.

**Why it is Highly Cohesive:**
Its only responsibility is notifying users about tasks.

---

# b) Coupling Analysis

Coupling refers to the level of dependency between components.
The design aims to achieve **low coupling**, meaning components interact through clear interfaces and minimal dependencies.

### Coupling Between Components

| Component   | Dependency    | Coupling Level | Explanation                                            |
| ----------- | ------------- | -------------- | ------------------------------------------------------ |
| TaskManager | TaskValidator | Low            | Only used for validation                               |
| TaskManager | ITaskStorage  | Low            | Uses interface rather than implementation              |
| TaskManager | TaskSearch    | Low            | Used for searching tasks                               |
| TaskManager | ITaskExporter | Low            | Export format can change without modifying TaskManager |
| TaskManager | TaskNotifier  | Low            | Only used for sending reminders                        |

### How Low Coupling Was Achieved

1. **Interfaces**

   Interfaces such as `ITaskStorage` and `ITaskExporter` ensure that TaskManager does not depend on concrete implementations.

2. **Dependency Injection**

   Dependencies are passed into the `TaskManager` constructor rather than created internally.

3. **Clear Component Boundaries**

   Each component focuses on a single responsibility and interacts through minimal interfaces.

---

### Coupling Improvements with More Time

If more time were available, the following improvements could further reduce coupling:

* Introduce an **INotifier interface** to allow multiple notification implementations (Email, SMS, Push notifications).
* Introduce **dependency injection frameworks** for better dependency management.
* Separate search functionality into its own **search service interface**.

---

# c) Single Responsibility Principle (SRP) Application

The Single Responsibility Principle states that a component should have **one reason to change**.

| Component      | Single Responsibility             | One Reason to Change           |
| -------------- | --------------------------------- | ------------------------------ |
| TaskManager    | Coordinate task operations        | Changes in task workflow       |
| TaskValidator  | Validate task data                | Changes in validation rules    |
| TaskRepository | Store and retrieve tasks          | Changes in storage mechanism   |
| TaskSearch     | Filter and search tasks           | Changes in search logic        |
| TaskExporter   | Export tasks to different formats | Changes in export format       |
| TaskNotifier   | Send task reminders               | Changes in notification method |

---

# Conclusion

The Task Management System follows modular architecture principles by ensuring:

* **High cohesion**: Each component focuses on a single responsibility.
* **Low coupling**: Components interact through interfaces and dependency injection.
* **SRP compliance**: Each component has one clear reason to change.

This modular design improves maintainability, scalability, and testability of the system.
