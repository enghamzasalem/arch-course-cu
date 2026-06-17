# Part 1.1 – Coupling Analysis

## Coupling Inventory

| Provider | Consumer | Direction | Coupling Type | Why Change Ripples |
|----------|----------|-----------|---------------|-------------------|
| Task API | Web SPA | → | Data + Temporal | SPA expects JSON format; API change breaks parsing |
| Task API | Mobile App | → | Data + Temporal | Mobile expects same response structure |
| Task API | Partner Integration | → | Data + Control | Partners rely on stable contract; any change requires partner updates |
| API Gateway | Task API | → | Deployment + Temporal | Gateway routes to specific API version; deployment must coordinate |
| Task API | Task Store | → | Data + Deployment | API expects certain schema; DB change may break queries |
| Task API | Notification Service | → | Control + Temporal | API calls Notify; Notify change may break reminders |
| Web SPA | API Gateway | → | Temporal | SPA waits for sync response; timeout or slow gateway affects UX |

---

## Intentionally Tight Coupling (Acceptable)

| Pair | Coupling Type | Why Acceptable |
|------|---------------|----------------|
| Task API ↔ Task Store | Data + Deployment | The store is owned by same team; changes are coordinated. Tight coupling is simpler and faster for internal components. |
| Web SPA ↔ API Gateway | Temporal | Web app needs immediate response; async would complicate UI. Sync request/response is the right pattern here. |

---

## Coupling to Reduce (Would Improve)

| Pair | Current Coupling | How to Reduce |
|------|------------------|---------------|
| Partner Integration ↔ Task API | Data (shared JSON shape) | Add version header or path prefix so partners can migrate gradually. Use allowlists for unknown fields. |
| Task API ↔ Notification Service | Control (direct call) | Use message queue. API publishes "task updated" event; Notify subscribes independently. Removes direct dependency. |

---

## Summary

- **Web SPA and Mobile** are tightly coupled to API response shape by necessity
- **Partners** are the highest risk: they cannot update as frequently as first-party clients
- **Internal coupling** (API ↔ Store) is acceptable because teams coordinate
- **Notification coupling** is a good candidate for decoupling via event bus