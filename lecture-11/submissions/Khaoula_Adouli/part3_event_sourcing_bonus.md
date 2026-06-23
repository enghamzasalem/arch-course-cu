# Part 3.3 — Event Sourcing (Bonus)

## Use Case: Order Lifecycle

CityBite can use event sourcing for order management.

### Events:
- OrderCreated
- PaymentProcessed
- OrderPrepared
- OrderDelivered

Instead of updating a single row, the system stores a sequence of events.

---

## Benefits

- Full history of order changes
- Easy debugging and auditing
- Ability to replay events after failure

---

## Recovery Scenario

If a bug occurs:
- Replay events
- Rebuild correct system state

---

## Trade-offs

- Increased complexity
- Requires careful design

---

## Conclusion

Event sourcing improves reliability and recovery but is not required for all parts of the system.