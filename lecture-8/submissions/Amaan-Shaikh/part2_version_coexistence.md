# Task 2.2 - Version Coexistence

## Strategy

For version coexistence, I would use header-based versioning with a custom `X-API-Version` header. The API Gateway reads this header and routes requests to the appropriate version handler. Path-based versioning adds `/v1` and `/v2` as a fallback for clients that prefer URLs.

## Client Usage During Migration

During the migration period, legacy clients continue using `/v1/tasks` or send `X-API-Version: 1`. New or updated clients use `/v2/tasks` or send `X-API-Version: 2`.

For example:
- Old client: `GET /v1/tasks` or `GET /tasks` with `X-API-Version: 1`
- New client: `GET /v2/tasks` or `GET /tasks` with `X-API-Version: 2`

The Gateway checks the header first, then falls back to the URL path. Clients that do not specify a version are routed to the latest stable version (v2 after migration starts). Both versions share the same database, with a transformation layer that converts `done` to `completed` and vice versa.

Both versions remain available during a 6-month sunset period. The API adds a `Deprecation` header to v1 responses starting at month 3. After most traffic has moved to v2, v1 can be deprecated and eventually return 410 Gone.

## Operational Cost

One operational cost of this approach is maintaining transformation logic between `done` and `completed` fields for the shared database. Another cost is the Gateway's routing complexity, which must check both headers and paths for each request.