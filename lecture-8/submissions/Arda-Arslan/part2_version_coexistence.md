# Task 2.2 - Version Coexistence

## Strategy

For version coexistence, I would use path-based versioning with /v1 and /v2 routes. This approach is simple and easy for clients to understand.

## Client Usage During Migration

During the migration period, legacy clients continue using /v1, while new or updated clients use /v2. For example, old clients call `/v1/tasks`, and new clients call `/v2/tasks`. The API Gateway routes requests based on the path, so both versions can run in parallel. Legacy clients that do not change their URLs automatically stay on v1 since their requests already point to /v1/tasks.

Both versions remain available during a sunset period. After most traffic has moved to v2, v1 can be deprecated and eventually removed.

## Operational Cost

One operational cost of this approach is maintaining two API versions at the same time, which increases testing and maintenance effort.