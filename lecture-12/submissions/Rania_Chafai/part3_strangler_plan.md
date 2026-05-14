# Part 3.1 — Strangler / Branch by Abstraction

## First Context to Extract

CityBite chooses to extract the **Notification Context** first.

### Reasons

- Lower business risk compared to payment or order processing
- Easier to isolate from the monolith
- High customer value through better notification reliability
- Allows the team to gain microservices experience safely

---

## Strangler Migration Plan

### Facade / Gateway

CityBite introduces an API gateway in front of the monolith.

The gateway routes:
- Notification requests to the new Notification Service
- All other requests to the existing monolith

---

### Traffic Ramp Strategy

The migration is performed gradually:

- 10% traffic → new service
- 50% traffic → new service
- 100% traffic → new service

This reduces deployment risk and allows safe monitoring.

---

## Rollback Trigger

CityBite rolls back to the monolith if:
- Notification error rate increases significantly
- Latency becomes unstable
- Message delivery failures exceed acceptable thresholds

---

## Branch by Abstraction

Before extraction, the monolith introduces a notification interface (port).

Example:
- NotificationSender interface
- SMSAdapter implementation
- EmailAdapter implementation

This decouples the Order service from concrete notification implementations and simplifies future extraction into a separate microservice.

This approach follows the ideas presented in `example1_flexibility_coupling_citybite.py`.