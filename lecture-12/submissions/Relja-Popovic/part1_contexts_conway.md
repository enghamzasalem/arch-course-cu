## Task 1.1

### Bounded Contexts

| Context | Ubiquitous language | Primary user | Owns |
|---|---|---|---|
| **Ordering** | cart, checkout, order, line item | Customer | Order lifecycle, order state machine, payment authorisation |
| **Restaurant** | menu, item, modifier, availability | Restaurant manager | Menu catalogue, restaurant profile, order acceptance |
| **Dispatch** | rider, assignment, route, ETA | Dispatcher / rider | Delivery assignment, rider location, notifications |

### Integration Between Adjacent Contexts

| Pair | Style | Why |
|---|---|---|
| Ordering → Restaurant | Sync API (menu read) + async event (`OrderPlaced`) | Menu reads at browse time need a live response; once an order is placed, the event notifies the restaurant asynchronously so checkout is not blocked on the tablet acknowledging |
| Ordering → Dispatch | Async event (`OrderConfirmed`) | Dispatch does not need to block checkout; rider assignment starts in the background once payment succeeds |
| Restaurant → Dispatch | Async event (`OrderReady`) | When a restaurant marks an order ready, Dispatch is notified to send the rider, one-way, no response needed |

### Conway's Law

Conway's Law says that the software a team builds tends to look like how that team is organised/their communication structure. If one team owns all of CityBite, they will naturally take shortcuts across context boundaries, e.g. querying the menu table directly from dispatch code, or adding a column to the orders table to serve a restaurant feature. Over time the three contexts blur into one big shared codebase. To get real separation, there will need to be either split in the team so each context has clear owners, or enforced rules that make crossing boundaries deliberately hard.
