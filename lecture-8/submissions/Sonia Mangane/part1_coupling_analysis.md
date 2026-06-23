# Task 1.1: Coupling inventory

I’ve identified five key relationships in our system. I’ve noticed that while some dependencies are necessary, others have serious implications. A small change in the provider could cause a lot of work for consumers.

| Component Pair | Direction | Coupling Type | Ripple Effect |
|----------------|----------|---------------|-----------------------------|
| Partner Client to Task API | Consumer to Provider | Data Coupling | Partners rely on specific JSON keys like `done`. If we rename it to `completed`, their code won't find the field and the UI might stop showing task status. |
| Task API to Task Store (DB) | Provider to Data | Schema Coupling | The API code expects specific table columns (like `title` and `id`). If a DBA renames a column in the database, the API’s SQL queries or ORM will fail immediately. |
| Task API to Notification Service | Service to Service | Temporal Coupling | Currently, the Task API waits for the Notification service to finish sending a reminder before it confirms a task was created. If the Notification service is down, task creation fails. |
| Web SPA to Task API | Consumer to Provider | Deployment Coupling | If the Web SPA is bundled with the API code, we can't update a button color on the web without re-deploying the entire backend, which increases the risk of downtime. |
| Mobile App to Task API | Consumer to Provider | Control Coupling | If the API returns a status like `403` and the Mobile App uses that specific code to decide to show a "Pay for Pro" popup, changing that logic on the server breaks the app's flow. |

## Places where coupling is intentionally tight (Acceptable)

### 1.  Task API & Task Store:
 I think it’s okay for these to be tightly coupled. The Task API’s whole job is to manage the Task data. Trying to make the API "database agnostic" with too many layers of abstraction usually just makes the code harder to read for a simple CRUD app.

### 2. Web SPA & Task API (Internal Contract)
Since our team owns both the Web SPA and the API, we can coordinate changes quickly. It’s "tighter" than the partner integration, but it allows us to move fast and add features without over-engineering versioning for our own internal tools.

## Places where I would reduce coupling

### 1. Task API & Notification Service (Move to Async): 
I would use a Message Broker here. The Task API should just trigger (and forget) an event saying a task was created. This removes the temporal Coupling, so the Task API stays fast and doesn't care if the Notification service is temporarily offline.

### 2.  Partner Integrations & Task API (Add a Gateway/Contract):
 I would introduce an API Gateway or a formal Versioned Contract. Currently, partners are coupled directly to our implementation. By putting a gateway in between, we can map old field names to new ones, allowing us to refactor our internal code without breaking their external integrations.