# Part 2.2 — Version Coexistence Strategy

## Chosen Strategy: Path Prefix (`/v1` and `/v2`) with Gateway Routing

### Rationale

Path prefix versioning makes the version explicit, visible, and immutable in every
request log, network trace, and bookmark. It requires no custom header negotiation
and works with all HTTP clients including `curl`, partner integrations, and browser
caches. A client can be certain which contract it is using by reading the URL.

The alternatives were considered and rejected:

- **Accept-Version header**: Invisible in URLs, cannot be bookmarked or linked, harder
  to enforce in third-party gateway products, and requires custom header documentation.
- **Subdomain** (`v2.api.example.com`): Requires separate TLS certificates, DNS
  changes, and CORS configuration per version. High operational cost for a migration.

---

## URL Structure

```
https://api.example.com/v1/tasks          (current clients, v1 contract)
https://api.example.com/v2/tasks          (new clients, v2 contract)
```

During the sunset period, both paths are live simultaneously. The API Gateway routes
based on the path prefix.

---

## What Changes in v2

v2 introduces all three MAJOR changes together rather than incrementally, to avoid
clients having to migrate twice:

- Field `done` renamed to `completed` (change B)
- Header `X-Client-Id` required (change C)
- Title max length enforced at 100 characters (change D)

Changes A (add `priority`) and E (add `POST /tasks/bulk`) are backward-compatible and
are released on both v1 and v2 simultaneously.

---

## Migration Flow

**Phase 1 — v2 launch (day 0):**
- v2 path goes live alongside v1.
- Sunset date for v1 is announced at launch: 12 months for first-party clients (web
  SPA, mobile), 18 months for partner integrations.
- All new features (change A, E) are added to both versions.
- v1 returns a `Deprecation` and `Sunset` HTTP response header on every request:
  ```
  Deprecation: true
  Sunset: Sat, 01 Mar 2026 00:00:00 GMT
  Link: <https://docs.example.com/migrate-v1-v2>; rel="deprecation"
  ```

**Phase 2 — active migration (months 1–12):**
- First-party clients (SPA, mobile) are updated to v2.
- Partners begin migration with documentation and sandbox access.
- v1 traffic is monitored; clients still using v1 are identified via `X-Client-Id`
  (optionally soft-enforced on v1 to identify callers before hard enforcement on v2).

**Phase 3 — v1 sunset (month 12–18):**
- v1 is locked: no new features, only critical security fixes.
- Partners who have not migrated are contacted directly.
- On sunset date, v1 returns `410 Gone` for all paths with a migration link in the body.

---

## Legacy Client Behaviour During Migration

Existing clients that do not update continue calling `/v1/tasks` exactly as before —
no code change required. They receive the `Deprecation` header in every response
(a low-friction warning), but their functionality is unaffected until the sunset date.

New clients are onboarded directly to v2.

---

## One Operational Cost

**Dual deployment and diverging codebases.**  
Running v1 and v2 simultaneously means the Task API service must either:

(a) Run as two separate deployable instances (v1-service and v2-service), each scaled
    independently — higher infrastructure cost, two deployment pipelines to maintain.

(b) Run as one service that branches on the version prefix internally — lower infra cost
    but internal complexity grows as v1 and v2 logic diverges over time.

The recommended approach is (a) for a long migration window (18 months): the clear
boundary between v1 and v2 codebases makes it easier to retire v1 cleanly. At sunset,
the v1 deployment is simply stopped and its infrastructure is decommissioned. With (b),
removal requires code surgery inside a live service.
