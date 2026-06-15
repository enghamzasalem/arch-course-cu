## Task 1.2

**User journey:** Place paid order (customer submits cart → payment authorised → order confirmed).

**SLI:** Proportion of checkout requests that return HTTP 2xx(success) with payment confirmed within 3 seconds, measured from API access logs over a 28-day window.

**SLO:** 99.5% of checkout requests meet the SLI each calendar month.

**Error budget:** The error budget is the 0.5% of requests CityBite is allowed to fail. When the burn rate is high, for example a 30-minute payment gateway outage consuming a week's budget in one incident, the team triggers a freeze: no non-critical feature deployments, no infrastructure changes until burn rate returns to baseline. If the budget is exhausted before month end, all deploys halt and an incident review is required before resuming. The budget is tracked in the monitoring dashboard so product and engineering share the same signal; a high burn rate is a product conversation, not only an on-call alert.