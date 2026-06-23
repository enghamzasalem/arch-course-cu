## Task 1.1: Coupling Inventory

- **Web SPA → Task API Service (Data coupling)**
  The SPA relies on specific JSON field names and HTTP status codes to display tasks. If the API renames a field or changes the error response format, the SPA will break without any warning until it is redeployed with updated code.

- **Mobile App → Task API Service (Data coupling + deployment coupling)**
  The mobile app is built against a fixed version of the API contract. Because app store releases take time, older versions of the app may still be making requests long after the API has changed, so both need to work at the same time.

- **API Gateway → Task API Service (Control coupling)**
  The gateway routes incoming requests to the Task API based on URL paths and version prefixes it knows about. If a new endpoint is added or a path changes, the gateway routing rules must be updated at the same time or requests will not reach the service.

- **Task API Service → Task Store (Data coupling)**
  The Task API reads and writes directly to the database using a specific schema. If a field is renamed or a new constraint is added to the database, the service queries will fail or return wrong data until the code is updated to match.

- **Task API Service → Notification Service (Temporal coupling)**
  When a task is marked as done, the Task API triggers a notification before responding to the client. If the Notification Service is slow or down, the whole task update is delayed or fails, even though the notification is not the main purpose of the request.

---

## Two Intentionally Tight Couplings

- **Task API Service → Task Store**
  This is acceptable because the Task API is the only service that should write to this database. Keeping them tightly linked ensures data consistency and makes the Task API the single responsible owner of all task data.

- **API Gateway → Task API Service**
  This is acceptable because the gateway needs to know where to send requests. Having this knowledge in one central place is simpler than asking each client to figure out routing on their own.

---

## Two Couplings to Reduce

- **Mobile App → Task API Service**
  Because old app versions cannot be updated instantly, a breaking API change forces the server to support incompatible clients at the same time. This can be improved by introducing URL versioning (e.g. `/v1/`, `/v2/`) so older app versions keep working while newer ones use the updated API.

- **Task API Service → Notification Service**
  Sending a notification inline during a task update means the update depends on the Notification Service being available. This can be improved by publishing an event to a message queue instead, so the task update completes immediately and notification delivery happens separately.