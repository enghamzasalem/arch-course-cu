# Task 2.2 - Cascading Failures and Circuit Breaker

## Retry storm narrative

The payment gateway starts returning HTTP 500 for some calls. Without protection, each checkout in the Order API retries up to five times before giving up. This is exactly what `example1_availability_circuit_breaker_citybite.py` shows: the naive loop multiplies the load on a sick partner. In the example, 60 checkouts cause far more than 60 gateway calls because every failed attempt triggers retries.

The same thing happens to our own service. Each retry holds a worker thread for several seconds while it waits for the gateway. When many checkouts retry at the same time, all our threads are busy waiting on a partner that is already in trouble. Healthy checkouts that arrive in the meantime cannot get a thread and time out. The DB connection pool also fills up because each stuck checkout is holding a transaction open. From the customer's view, the whole app slows down, even features that have nothing to do with payment. This is a cascading failure: the partner outage spreads into our own API because of the way we retry.

## Circuit breaker policy

**Thresholds**: the breaker opens after 5 consecutive failures on the payment gateway, or if the failure rate over the last 30 seconds is above 50%. We count timeouts as failures too, not only HTTP errors. The numbers are not magical, they just need to be high enough to ignore short blips and low enough to react before the queue fills up.

**Open duration**: when open, the breaker fails fast for 30 seconds. During this time no real call goes to the gateway, so we stop adding load to a sick partner. After 30 seconds the breaker goes to half-open and lets one trial call through. If it succeeds the breaker closes again, if it fails the breaker reopens for another 30 seconds.

**Fallback**: when the breaker is open, we do not just show an error. The checkout switches to a "pay later" path: the order is saved with status "pending payment", the customer gets a clear message ("payment is taking longer than usual, we will charge you in a few minutes"), and a worker retries the payment in the background once the breaker closes. If the customer is not comfortable with that, they can cancel. This way we keep some checkouts even during a partner outage, and we are honest about what is happening.

## Timeouts and bulkhead

**Timeouts**: every call to the payment gateway has a hard timeout (for example 3 seconds). Without a timeout, a slow gateway is worse than a failing one, because the thread waits forever and the breaker never sees a failure to count. Timeouts turn "slow" into "failed" so the breaker can do its job.

**Bulkhead**: each external dependency gets its own connection pool, separate from the others. The payment gateway has a pool of, say, 20 connections; the maps API has its own pool; the DB has its own pool. If the payment gateway gets stuck, only that pool fills up. The DB pool and the maps pool are still free, so other parts of the app keep working.

These pair with the breaker because each pattern fixes a different problem. The breaker stops calling a sick partner. The timeout makes sure we notice when a call is sick. The bulkhead makes sure one sick partner cannot drag down everything else. Without all three, you can still cascade: a breaker with no timeout never trips, and a breaker with no bulkhead still lets the gateway eat all your threads before it opens.

## Canary request

A canary request, in the lecture sense, means sending a risky or suspicious piece of work to one worker first, before fanning it out to the rest of the fleet. The point is to protect the workers from a poison message: if the canary worker crashes or hangs, only one is affected and the others stay healthy.

In CityBite this fits the **bulk menu import** flow. Restaurants sometimes upload large menu files (hundreds of items, images, weird formatting). A bad file can crash the parser, and if we send the same file to many workers in parallel, all of them die at once. So the first time we see a new menu file, we send it to one worker only. If that worker finishes cleanly, we know the file is safe and we can process the rest of the work normally. If the canary worker fails or times out, we mark the file as bad and do not touch the other workers. The blast radius is one worker instead of the whole fleet.

In the normal checkout flow this pattern does not apply per request, because every order is just regular user input and not a "risky payload". The canary idea is for work items that could be dangerous to all workers if processed naively.