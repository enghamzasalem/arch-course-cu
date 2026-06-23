## Task 2.2: Version coexistence

## Strategy: Path Prefix (`/v1`, `/v2`)

All existing endpoints are served under `/v1/tasks`, and the updated API is served under `/v2/tasks`. The API Gateway inspects the URL prefix and routes each request to the appropriate version of the Task API Service. Both versions run simultaneously during the migration period.

---

## How v1 and v2 Coexist

**Legacy clients** (web SPA, mobile apps, partners) continue sending requests to `/v1/tasks` unchanged. They keep using `done`, are not required to send `X-Client-Id`, and the 500-character title limit remains in effect. No changes are needed on their side until the sunset date.

**New clients** are onboarded directly to `/v2/tasks`, which reflects all breaking changes: `completed` replaces `done`, `X-Client-Id` is required on every request, and the title limit is 100 characters.

The sunset period gives legacy clients a fixed window, for example 6 months, to migrate to v2. During this time, `/v1` returns a `Deprecation` response header on every reply to signal that the version is scheduled for removal. At the end of the sunset period, the gateway stops routing `/v1` traffic and returns a `410 Gone` response directing clients to `/v2`.

---

## Operational Cost

Running both versions simultaneously requires maintaining two separate routing rule sets in the gateway and keeping the v1 service code alive and patched for the full duration of the sunset period, even if no new features are being developed for it. Any security fix or infrastructure update must be applied to both versions independently until v1 is retired.