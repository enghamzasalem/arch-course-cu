## Part 1.1: Component Design Rationale

The system is decomposed into five primary components to ensure a Separation of Concerns (SoC). By isolating "what" the system does from "how" it does it, we achieve a modular architecture that is easier to maintain and extend.

### 1. TaskValidator

**Responsibility:**  
The `TaskValidator` component is responsible for checking if the task data is valid before it is stored in the system. It verifies things like whether the task has a title and whether required fields are filled.

**Rationale:**  
Keeping validation in a separate component makes the system easier to maintain. All validation rules are handled in one place, which prevents invalid data from reaching other parts of the system like the repository or notifier. If validation rules change, we only need to update this component.

---

### 2. TaskRepository

**Responsibility:**  
The `TaskRepository` manages how tasks are stored and retrieved. It handles operations such as adding tasks, deleting tasks, and listing all tasks.

**Rationale:**  
Separating the storage logic from the rest of the system allows the application to stay independent of how data is stored. By using an interface (`ITaskRepository`), different storage implementations such as in-memory storage or file storage can be swapped without changing the `TaskManager`.

---

### 3. TaskSearch

**Responsibility:**  
The `TaskSearch` component provides functionality for filtering and searching tasks based on different conditions like keyword, assignee, or status.

**Rationale:**  
Search functionality is separated from the main task management logic so it can be modified or improved independently. This makes it easier to add new filtering features or improve search performance without affecting other components.

---

### 4. TaskExporter

**Responsibility:**  
The `TaskExporter` is responsible for converting tasks into external formats such as JSON or CSV.

**Rationale:**  
Exporting data is a separate concern from managing tasks. By isolating export functionality in its own component, new export formats can be added easily without modifying the core system logic.

---

### 5. TaskNotifier

**Responsibility:**  
The `TaskNotifier` handles sending reminders or notifications related to tasks. In this project, notifications are simulated using console output.

**Rationale:**  
Notification logic is separated so that changes to how notifications are sent do not affect other parts of the system. For example, the system could later switch from console messages to email or messaging services without modifying the core task management logic.

### 6. TaskLogger

**Responsibility:**
The `TaskLogger` is responsible for recording system events and operations (such as task creation, deletions, or export actions). It provides "Observability" by tracking the state of the application during execution.

**Rationale:**
Logging is a cross-cutting concern that is isolated to prevent "code bloat" within other components. By using an `ILogger` interface, the `TaskManager` remains agnostic about where logs are stored. This allows the system to easily pivot from simple console logging to writing to a persistent `.log` file or an external cloud monitoring service (like Datadog or AWS CloudWatch) without changing the orchestrator's code.