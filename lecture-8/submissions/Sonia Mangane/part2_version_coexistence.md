# Task 2.2: Version coexistence


## 2.1 Strategy: URL Path Versioning

We will use a **Path Prefix strategy**: `/v1/tasks` and `/v2/tasks`.

- **v1:** We keep this exactly as it is now. No X-Client-Id required, 500-character titles allowed, and the field is still called done.

- **v2:** This is where we break things for the better. We rename done to completed, tighten the title limit to 100 characters, and make the X-Client-Id header mandatory.


## 2.2 How We Move Everyone Over

We cannot break existing clients abruptly, so we follow a slow migration plan:

1. The Coexistence Phase: For the next 6 months, both versions will live on our servers at the same time.

2. Smart Routing: We’ll configure our API Gateway to look at the URL. If it see /v1/, it sends the request to our legacy code. If it sees /v2/, it goes to the new code.

3.  New Clients: Starting today, we update our Swagger docs so that /v2/ is the default. Any new partner signing up only gets the documentation for v2.

4. The Sunset Warning: After 3 months, we’ll start sending a Warning header in the v1 responses. It won't break their code, but their developers will see deprecated messages in their logs, which should nudge them to upgrade.


## 2.3 Dual Logic Maintenance

The main operational cost is **maintenance double-duty**.

Since we have two versions of the API, every time we find a bug—like a security flaw in how tasks are saved—we have to fix it in two places. We have to write tests for the v1 logic and the v2 logic. It basically doubles our work for every "Task" related feature until we finally turn off v1. If we aren't careful, v1 might get "stale" and behave differently than v2, which would be a nightmare to debug.