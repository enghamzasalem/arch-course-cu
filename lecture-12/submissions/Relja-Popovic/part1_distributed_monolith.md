## Task 1.2

| Red flag | What it looks like in CityBite | Mitigation |
|---|---|---|
| **Shared database** | Ordering, Restaurant, and Dispatch all read and write the same Postgres schema; a schema change for one context breaks the others | Give each context its own schema or database; cross-context data access must go through an API or event, never a direct table join |
| **Synchronous chain of calls** | A customer checkout triggers a sync call to Restaurant to validate the menu, which triggers a sync call to Dispatch to pre-assign a rider. The whole chain must succeed for checkout to return | Replace the chain with async events; Restaurant and Dispatch react independently; checkout only waits on payment |
| **Lockstep deploys** | Deploying a change to the Dispatch service requires coordinating a simultaneous deploy of Ordering because they share a contract with no versioning | Apply the additive-change rule from `example2`: add fields and never remove or rename them. Each service can deploy independently as long as consumers use tolerant JSON readers |