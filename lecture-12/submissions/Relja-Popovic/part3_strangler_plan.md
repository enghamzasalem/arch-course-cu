## Task 3.1

### Context to Extract: Restaurant

**Risk:** Restaurant is read-heavy (menu browsing) and mostly independent. It does not hold payment state, so a failure during extraction does not risk money or order integrity. Therefore, it is the safest first extraction.

**Team value:** A dedicated Restaurant team can iterate on menu features (modifiers, availability toggles, image uploads) without touching the Ordering codebase or coordinating deploys.

**Customer value:** Faster menu load times and more reliable availability updates directly improve the browse experience, which is the first thing every customer sees.

### Strangler Plan

**Facade:** An API gateway sits in front of both the monolith and the new Restaurant service. All traffic initially routes to the monolith.

**Traffic ramp:**
1. 0% → new service: facade routes all `/restaurants/*` and `/menu/*` calls to the monolith.
2. 10% → new service: internal staff and beta restaurant managers only.
3. 50% → new service: monitor error rate and p95 latency; compare against monolith baseline.
4. 100% → new service: monolith Restaurant code is deleted; facade rule updated.

**Rollback trigger:** If error rate on the new service exceeds 1% or p95 latency is more than 200 ms above the monolith baseline at any ramp stage, the facade instantly routes 100% back to the monolith.

### Branch by Abstraction

Before splitting Restaurant out, introduce a `RestaurantPort` interface inside the monolith, the same pattern as `PaymentPort` in `example1`. All Ordering code that currently imports Restaurant logic directly is rewritten to call `RestaurantPort` instead. The monolith implementation is the default. When the new Restaurant service is ready, HTTP client is swapped in behind the same interface. No Ordering code changes at split time, only the adapter is replaced, like `OrderServiceLoose` swaps payment adapters without knowing the difference.