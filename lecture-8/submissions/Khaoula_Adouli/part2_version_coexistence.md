# Part 2.2 - Version Coexistence Plan (v1 + v2)

## Chosen strategy
During the coexistence period, both v1 and v2 are deployed and served in parallel through the API Gateway, which routes requests based on the versioned path.

I choose a **hybrid strategy**:

1. **Path versioning** for clarity:
   - `/api/v1/tasks`
   - `/api/v2/tasks`
2. **Gateway routing policy**:
   - API Gateway routes traffic to Task API v1 or Task API v2 services.
3. Optional header for observability only:
   - `X-Client-Id` is tracked in both versions during migration; it is optional (warning-only) in v1 and strictly required in v2.

## Why this strategy

- Path versioning is explicit and easy for partners, docs, and testing.
- Gateway centralizes migration controls (routing, metrics, deprecation warnings).
- Separate v1/v2 deployments avoid risky "if version then behavior" branching inside one code path.

## Coexistence timeline

### Phase 0 - Preparation
- Publish v2 OpenAPI/docs and migration guide.
- Add telemetry in v1 for field usage (`done`, long titles, missing `X-Client-Id`).

### Phase 1 - Dual running (sunset announced)
- v1 remains fully operational at `/api/v1`.
- v2 is introduced at `/api/v2`.
- Gateway adds response headers on v1:
  - `Deprecation: true`
  - `Sunset: <date>`
  - `Link: <migration guide URL>; rel="deprecation"`

### Phase 2 - Migration pressure
- First-party web/mobile move to v2 first.
- Partner clients receive direct communication and a support checklist.
- For v1, gateway can emit warning events for calls still using `done`.

### Phase 3 - Sunset
- After notice period (example: 90 days), v1 is deprecated and eventually disabled; all requests return a clear error indicating that the version is no longer supported.
- Final cutoff date: v1 returns a structured error for blocked operations.

## How new vs legacy clients are handled

- **New clients:** must use `/api/v2/*`.
- **Legacy clients:** continue `/api/v1/*` for the sunset window.
- SDKs:
  - New SDK default target = v2.
  - Legacy SDK branch remains supported with security fixes until sunset.

## Operational cost (required)

Main cost: **dual operation burden**:
- two API versions to deploy and monitor,
- duplicate docs/examples/testing matrix,
- gateway routing and policy complexity,
- support load while partners migrate.

This cost is acceptable because it prevents uncontrolled client breakage and supports predictable migration.
