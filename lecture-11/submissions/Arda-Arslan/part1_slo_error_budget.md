# Task 1.2 - SLI, SLO, and Error Budget

## User journey

The chosen journey is "place paid order". A customer opens the app, fills the cart, taps pay, the payment is charged, and the order is confirmed to the restaurant. This is the most important journey for CityBite because it is where the money is made and where most external dependencies are touched at once (API, DB, payment gateway, SMS).

## SLI

Successful checkout ratio.

Definition: number of checkout attempts that reach the "confirmed and paid" state, divided by total checkout attempts in the same time window.

How we measure it: from the order record in the database, not from the HTTP response. A checkout counts as successful only if the order ends up stored with status "confirmed" and the payment is marked as captured. A 200 response from our API is not enough, because the payment can still fail or the worker can fail to push the order to the restaurant. We track the final order state in metrics and break failures down by cause (gateway decline, gateway timeout, DB error, restaurant push failure) so we can see where we lose users.

## SLO

99.5% of checkout attempts reach the confirmed and paid state, measured over a rolling 30 day window.

This means we allow about 0.5% failed checkouts per month. Out of 100,000 checkouts, 500 can fail before we are out of budget.

## Error budget

The error budget is the 0.5% we are allowed to "spend" on failures in a 30 day window. It is what makes the SLO useful, because instead of chasing 100% (impossible and expensive) we accept some failures and watch how fast we use them up.

Burn rate is how quickly we consume the budget. If we lose 0.5% in a few hours, we are burning the entire month in one day, which is a serious incident.

What we do when burn rate is high:
- Freeze deploys for the affected service so we do not add new bugs while fighting the fire.
- Stop launching new features that touch checkout (pause feature flags, hold releases).
- Open an incident and focus the team on root cause and fix.
- If the budget is fully spent before the window ends, deploys stay frozen until the next window or until reliability work brings the SLI back inside the SLO.

This way the SLO is not just a number on a dashboard. It changes what the team is allowed to do.