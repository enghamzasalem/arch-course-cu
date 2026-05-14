# Part 1.2 — SLI / SLO / Error Budget

## Chosen User Journey: "Place a Paid Order"

This part covers the full checkout path: a customer submits their cart, the Order API validates the order, charges the payment gateway, persists the order to Postgres, and returns a confirmation. It is the highest-value interaction in CityBite — if it fails, no revenue is generated.

---

## SLI Definition

**SLI:** The proportion of checkout requests that complete successfully within an acceptable latency window.

```
SLI = (number of POST /orders requests that return HTTP 2xx within 3 seconds)
      ─────────────────────────────────────────────────────────────────────────
      (total number of POST /orders requests)
```

**How it is measured:** Application logs and the API gateway emit a structured log line for every request containing `status_code` and `duration_ms`. A metrics pipeline (e.g. Prometheus + a recording rule) aggregates these over a rolling 5-minute window and exposes the ratio as a gauge. Requests that time out at the gateway count as failures even if the backend eventually responds.

---

## SLO Definition

**SLO:** 99.5% of checkout requests succeed (as defined by the SLI above) over any rolling 30-day window.

| Attribute | Value |
|-----------|-------|
| Journey | Place a paid order (`POST /orders`) |
| SLI metric | Successful checkouts / total checkouts |
| Target | **99.5%** |
| Window | Rolling 30 days |
| Measurement source | API gateway access logs + Prometheus |

A 99.5% SLO means CityBite tolerates at most **0.5% failed checkouts** per month. Over a 30-day month (43,200 minutes), that is roughly **216 minutes of equivalent full-outage budget**, or a proportionally larger number of partial failures spread across the month.

---

## Error Budget

The **error budget** is the allowed failure headroom before the SLO is breached:

```
Error budget = 1 − SLO target = 1 − 0.995 = 0.5%
```

If CityBite processes 500,000 checkout attempts per month, the error budget is **2,500 failed checkouts**.

### Burn Rate and Consequences

| Burn Rate | Meaning | Action |
|-----------|---------|--------|
| < 1× | Budget consumed slower than it replenishes | Normal operations; feature work continues |
| 1–2× | Budget on track to be exhausted by month end | Engineering team is alerted; investigate root cause |
| > 2× (fast burn) | Budget will be exhausted in < 15 days | **Feature freeze**: no new deployments until burn rate drops below 1× |
| > 5× (critical burn) | Budget exhausted in < 3 days | **Deploy freeze + incident declared**: on-call team focuses exclusively on stabilisation; rollback last deployment if correlated |

### Why Error Budgets Matter

The error budget creates a shared contract between product and engineering. When the budget is healthy, the team has confidence to ship features and run experiments. When the budget is burning fast, it is an objective signal — not a judgment call — that reliability work takes priority over new features. This removes the subjective argument of "is it stable enough to ship?" and replaces it with a measurable answer.
