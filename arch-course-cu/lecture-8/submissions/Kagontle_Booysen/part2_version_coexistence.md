# Part 2.2: Version Coexistence Plan

---

## 1. Chosen Strategy — Path Prefix Versioning (Hybrid with Header Fallback)

**Primary mechanism:** URL path prefix — `/v1/tasks` for the current contract, `/v2/tasks` for the new contract.

**Hybrid addition:** The API gateway also accepts an `API-Version: 2` request header on the unversioned `/tasks` path during the transition period. This allows first-party clients (Web SPA, Mobile app) to opt into v2 behaviour incrementally by header alone, without requiring a URL change in every API call. Partner integrations are required to migrate to the explicit `/v2/` path prefix by the sunset date — they may not rely on the header shortcut.

### Why path prefix over alternatives

| Strategy | Reason accepted / rejected |
|----------|---------------------------|
| **Path prefix** (`/v1`, `/v2`) | ✓ Chosen. Explicit in URLs, visible in logs and gateway routing rules, easy to document for partners, requires no client-side header negotiation logic. |
| `Accept` / `Accept-Version` header | Rejected as primary. Headers are invisible in browser address bars and proxy logs, making debugging harder. Partners with simple HTTP clients often strip custom headers. |
| Separate subdomain (`v2.api.example.com`) | Rejected. Requires separate TLS certificates, separate DNS entries, and separate gateway deployments — operational cost is too high for a two-version coexistence window. |
| Feature flags / per-client negotiation | Rejected. Adds server-side complexity (flag store, per-client state) and makes behaviour unpredictable for partners who cannot inspect the flag state. |

---

## 2. How v1 and v2 Coexist

### Routing at the gateway

The API gateway routes requests based on the URL path prefix:

```
/v1/tasks       →  Task API service  (v1 handler)
/v1/tasks/{id}  →  Task API service  (v1 handler)
/v2/tasks       →  Task API service  (v2 handler)
/v2/tasks/{id}  →  Task API service  (v2 handler)
/v2/tasks/bulk  →  Task API service  (v2 handler, change E)
```

The Task API service runs a **single deployment** with both handlers active. There is no separate v1 and v2 process — the version is resolved at the handler layer inside the same service. This avoids dual deployment while maintaining clean contract separation.

```
┌─────────────┐     /v1/*     ┌─────────────────┐     v1 handler
│ Legacy      │ ──────────► │                 │ ──────────────►  Task store
│ clients     │             │  API gateway    │
│ (partners,  │     /v2/*   │  (routes by     │     v2 handler
│ old mobile) │ ──────────► │  path prefix)   │ ──────────────►  Task store
└─────────────┘             └─────────────────┘
```

### What changes between v1 and v2

| Contract element | v1 behaviour | v2 behaviour |
|-----------------|-------------|-------------|
| Task completion field | `done` (boolean) | `completed` (boolean) — change B |
| `X-Client-Id` header | Optional | Required — change C |
| `title` max length | 500 characters | 100 characters — change D |
| `priority` field | Not present | Optional on responses — change A |
| Bulk create | Not available | `POST /v2/tasks/bulk` — change E |

v1 contract is **frozen** on the day v2 is released. No new features are added to v1 after that point. Only critical security patches may be applied to v1 during the sunset window.

### Legacy clients stay on v1

Existing clients — partners, old mobile builds, the current Web SPA — continue calling `/v1/tasks` with no changes required. Their requests are routed to the v1 handler which continues to:

- Return `done` instead of `completed`
- Accept requests without `X-Client-Id`
- Accept `title` up to 500 characters
- Not return `priority`

This gives legacy clients a **minimum 12-month sunset window** from the v2 release date to migrate at their own pace.

### New clients adopt v2

New Web SPA builds, updated mobile releases, and newly onboarded partners call `/v2/tasks` from day one. They:

- Send and receive `completed` instead of `done`
- Always include `X-Client-Id`
- Enforce `title` ≤ 100 characters on their side before sending
- Optionally display `priority` in the UI
- May use `POST /v2/tasks/bulk` for batch operations

### Sunset timeline

| Milestone | Action |
|-----------|--------|
| v2 release day | `/v2/tasks` goes live; v1 frozen; deprecation notices added to v1 response headers (`Deprecation: true`, `Sunset: <date>`) |
| Month 1–3 | Partners notified by email with migration guide; mobile app update submitted to app stores |
| Month 6 | v1 traffic report published internally; partners still on v1 contacted directly |
| Month 12 | v1 sunset date — `/v1/tasks` returns `410 Gone` with a migration pointer in the response body |
| Month 13+ | v1 routing rules removed from gateway; v1 handler removed from codebase |

---

## 3. Operational Cost — Dual Handler Maintenance in a Single Codebase

Running v1 and v2 inside the same service avoids a full dual deployment, but it introduces **dual handler maintenance**: every bug fix, security patch, or infrastructure change (e.g. database connection pooling, logging format, auth middleware) must be applied to both the v1 and v2 handler paths and regression-tested against both contracts simultaneously.

This cost compounds as the sunset window lengthens. If partners are slow to migrate and the window extends beyond 12 months, the team carries two active contract implementations for longer than planned. The v1 handler also holds back schema simplifications — for example, the database cannot drop the old `done` column until v1 is fully retired, because the v1 handler still reads and writes it.

**Mitigation:** Set a hard sunset date at v2 launch (not a soft target), publish it in the `Sunset` response header from day one, and enforce it. Make the cost of extension visible to stakeholders by tracking the number of active v1 callers monthly and reporting it as a technical debt metric.

---


