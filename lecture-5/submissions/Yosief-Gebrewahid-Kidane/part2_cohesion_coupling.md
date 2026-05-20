# Part 2.2 – Cohesion and Coupling Analysis

## Component Diagram

The following diagram illustrates the modular architecture of the Task Management System.

![Component Diagram](part2_component_diagram.png)

---

# a) Cohesion Analysis

Cohesion describes how strongly related the responsibilities inside a component are.  
High cohesion means that a component focuses on a **single well-defined responsibility**.

---

## TaskManager

**Type of Cohesion:** Functional Cohesion

TaskManager acts as the central coordinator of the system. It manages the workflow of creating, validating, storing, searching, and exporting tasks by interacting with other components.


---

## TaskValidator

**Type of Cohesion:** Functional Cohesion

TaskValidator is responsible for validating task data before tasks are stored or processed.

Since the component performs only validation-related tasks, it exhibits high cohesion.

---

## TaskSearch

**Type of Cohesion:** Functional Cohesion

TaskSearch is responsible for searching and filtering tasks according to different criteria such as status or title.

All operations within this component are related to searching tasks, which makes the component highly cohesive.

---

## TaskNotifier

**Type of Cohesion:** Functional Cohesion

TaskNotifier handles sending notifications or reminders related to tasks.

Because its responsibilities are limited to task notifications, the component maintains strong functional cohesion.

---
## TaskRepository

**Type of Cohesion:** Functional Cohesion

TaskRepository is responsible for storing and retrieving tasks.  
Its operations include adding, retrieving, listing, and deleting tasks.

All methods focus on task persistence, which gives the component high functional cohesion.

## TaskExporter

**Type of Cohesion:** Functional Cohesion

TaskExporter is responsible for exporting tasks to external formats.

Different implementations such as JSON and CSV exporters follow this interface, but their core responsibility remains exporting task data.
** This ensures strong functional cohesion**

---

# b) Coupling Analysis

Coupling describes the level of dependency between components in a system.  
A well-designed system aims to maintain **low coupling**, meaning that changes in one component have minimal impact on others.

The Task Management System achieves low coupling through **interfaces, dependency injection, and modular design**.

---

## TaskManager and Other Components

TaskManager interacts with:

- TaskValidator
- TaskSearch
- TaskNotifier
- ITaskRepository
- ITaskExporter

**Coupling Level:** Medium

TaskManager must coordinate multiple components to perform task operations. However, it communicates with repository and exporter components through interfaces instead of concrete implementations. This reduces direct dependency on specific classes.

---

## TaskManager and Repository Interface

TaskManager depends on the **ITaskRepository interface** rather than specific repository implementations.

**Coupling Level:** Low

Because of this abstraction, the repository implementation can be changed without modifying TaskManager.

---

## TaskManager and Exporter Interface

TaskManager interacts with the **ITaskExporter interface**.

**Coupling Level:** Low

This allows different exporter implementations, such as JsonExporter or CsvExporter, to be used interchangeably without changing the TaskManager.

---

## TaskSearch and Repository

TaskSearch depends on the repository to retrieve tasks for filtering and searching.

**Coupling Level:** Medium

Although TaskSearch depends on repository data, it interacts through the repository interface, which allows the storage mechanism to change without modifying the search logic.

---

## Implementation and Interface Relationships

Repository and exporter implementations depend on their respective interfaces.

Examples include:

- InMemoryTaskRepository → ITaskRepository
- FileTaskRepository → ITaskRepository
- JsonExporter → ITaskExporter
- CsvExporter → ITaskExporter

**Coupling Level:** Low

This design ensures that new implementations can be added without affecting existing components.

---

## Techniques Used to Reduce Coupling

The system reduces coupling using the following techniques:

- Interface-based design
- Dependency injection
- Separation of responsibilities
- Modular component structure

These techniques ensure that components interact through clearly defined contracts rather than direct dependencies.

---

## Possible Improvements

With more development time, coupling could be further reduced by:

- Introducing an interface for TaskNotifier
- Using an event-driven architecture for notifications
- Adding a service layer between TaskManager and other components

These improvements would make the system even more flexible and scalable.

---

# c) Single Responsibility Principle (SRP)

The system follows the **Single Responsibility Principle**, meaning each component has a single well-defined responsibility and one reason to change.

| Component | Responsibility | One Reason to Change |
|-----------|---------------|----------------------|
| TaskManager | Coordinates task operations | Changes in workflow logic |
| TaskValidator | Validates task data | Changes in validation rules |
| TaskRepository | Stores and retrieves tasks | Changes in storage mechanism |
| TaskSearch | Searches and filters tasks | Changes in search logic |
| TaskExporter | Exports tasks to external formats | Changes in export formats |
| TaskNotifier | Sends task notifications | Changes in notification mechanism |

