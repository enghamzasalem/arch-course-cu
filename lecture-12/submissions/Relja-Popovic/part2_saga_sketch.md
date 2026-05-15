## Task 2.3

**Journey:** Place paid order

### Local Steps and Compensating Actions

| Step | Context | Local action | Compensating action if a later step fails |
|---|---|---|---|
| 1 | Ordering | Create order with status `PENDING` | Delete order record |
| 2 | Ordering | Authorise payment via Payment gateway | Issue refund / void authorisation |
| 3 | Restaurant | Accept order, mark kitchen queue | Cancel order on restaurant tablet |
| 4 | Dispatch | Assign rider | Unassign rider, return to pool |
| 5 | Ordering | Set order status to `CONFIRMED` | final step, no compensation needed |

### Choreography vs Orchestration

**Choice: Choreography** - each context listens for events and reacts independently with no central coordinator.

**Pros:**
- Each context stays loosely coupled. Adding a new step means subscribing a new service to an existing event, not modifying a central orchestrator.
- No single point of failure. If the orchestrator crashes in an orchestration approach, everything stalls.

**Con:**
- The overall flow is implicit. It lives in the sum of all event subscriptions rather than in one readable place, which makes debugging and tracing a failed saga harder.