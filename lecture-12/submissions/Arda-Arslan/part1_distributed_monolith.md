# Task 1.2 - Distributed monolith check

If CityBite splits the codebase into separate services but keeps doing the things below, the result is not really microservices, it is a distributed monolith.

## Red flag 1 - Shared database

All "services" still read and write the same Postgres tables. The rule for real microservices is database per service. If Orders and Payments both do SQL joins on the same `orders` table, a schema change in one team breaks the other team's deploy. The services share a fate even if they run in separate pods.

**Mitigation (tech + boundary):** give each context its own logical schema (or its own database), and forbid cross-context SQL joins. Integration only via APIs or events. If Orders needs payment info for a screen, it calls the Payments API instead of joining the table.

## Red flag 2 - One release train

You cannot deploy Payments on Tuesday without also deploying Orders and Dispatch. Releases are coordinated, with a shared staging cycle and a shared "go / no-go" meeting. You pay the cost of distribution (network, timeouts, idempotency) but get none of the benefit, which is independent velocity per team.

**Mitigation (process):** one independent CI/CD pipeline per service, with its own version, its own deploy schedule, and consumer-driven contract tests so that a service can release without waiting for the others. If a service cannot be deployed alone safely, the boundary is wrong.

## Red flag 3 - Synchronous chains between services

A single user request goes Orders -> Payments -> Dispatch -> Notifications, all sync HTTP, all in one call stack. If Notifications is slow, the customer sees a slow checkout. If Dispatch is down, the order fails. This is the same kind of tight coupling as a shared database, just moved from the data layer to the call layer: one outage cascades through everything and independent velocity is lost.

**Mitigation (boundary + tech):** keep sync only where the answer is needed right now (Orders -> Payments at checkout). For everything else - notifications, dispatch handoff, receipts - use async events. The caller does not wait, and a downstream outage does not bring down the order flow.