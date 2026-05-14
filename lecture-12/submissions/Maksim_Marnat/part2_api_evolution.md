# Part 2.2 — Public API evolution (CityBite, `GET /orders/{id}`)

Endpoint: **`GET /v1/orders/{orderId}`** — JSON for mobile **order detail** screen.

**v1 contract (stable keys, cf. `order_v1` in `example2_flexibility_api_evolution_citybite.py`):** `orderId`, `totalCents`, `status` — additive work **only adds** keys; never remove or rename these in v1.

## Two additive changes (safe for old clients)

Aligned with `order_v1_additive` in `example2_flexibility_api_evolution_citybite.py`: **new optional keys**; tolerant parsers ignore unknown fields.

1. **`estimatedDeliveryMinutes`** (nullable integer) — populated when dispatch projection knows ETA; old app ignores key, UI unchanged.
2. **`paymentSummary`** (object, optional) — `{ "state": "CAPTURED" | "PENDING", "lastFour": "4242" }`; old clients only read legacy `status` and remain valid.

## One breaking change — versioning & deprecation

**Breaking:** Rename **`orderId` → `id`** and **`totalCents` → `total_cents`** (same failure mode as `order_v2_breaking_rename` in **example2**).

**Versioning:** Ship **`GET /v2/orders/{orderId}`** (path param unchanged for mobile routing); **response body** uses the **`order_v2_breaking_rename`** shape (`id`, `total_cents`, `state`). **v1** frozen except additive fields. **`Accept: application/vnd.citybite.order+json; version=2`** optional later.

**Deprecation:** Announce **90-day** sunset: telemetry on **v1** traffic; after window, **410 Gone** with JSON `upgradeUrl` to force store update.

## Consumer-driven contract (one sentence)

**Mobile teams publish** expected JSON fixtures (Pact-style); **Order BFF / API** verifies them in CI so server changes cannot silently break production clients.
