# Task 2.1 - Change Classification

## A - Add optional JSON field `priority` to GET /tasks response

- **Breaking or non-breaking:** Non-breaking  
Adding an optional field does not affect existing clients that ignore unknown fields.  
This assumes clients are tolerant of unknown fields, overriding the strict-client default.

- **Semver:** MINOR  
This is an additive, backward-compatible change.

- **Semantic risk:**  
Clients may start showing or sorting tasks differently if they assume the new `priority` field should influence task order or importance.

## B - Rename JSON field `done` -> `completed` in responses

- **Breaking or non-breaking:** Breaking  
Existing clients expecting the `done` field will fail to read the response correctly.

- **Semver:** MAJOR  
Renaming a field breaks the API contract for existing clients.

- **Semantic risk:**  
Some clients may treat tasks as incomplete or show the wrong status if they still read only `done` and ignore `completed`.

## C - Require new header `X-Client-Id` on all requests

- **Breaking or non-breaking:** Breaking  
Existing clients that do not send this header will have their requests rejected.

- **Semver:** MAJOR  
Introducing a new required input breaks compatibility.

- **Semantic risk:**  
Requests from older clients may be rejected or handled differently because the server now depends on client identification that was not required before.

## D - Change `title` max length from 500 to 100 characters

- **Breaking or non-breaking:** Breaking  
Requests that were previously valid may now be rejected due to stricter validation.

- **Semver:** MAJOR  
This change alters the accepted input constraints.

- **Semantic risk:**  
Users may lose part of the title or see new validation errors for task names that were previously accepted by the system.

## E - Add `POST /tasks/bulk` with new request shape

- **Breaking or non-breaking:** Non-breaking  
Adding a new endpoint does not affect existing clients.

- **Semver:** MINOR  
This is a backward-compatible addition of new functionality.

- **Semantic risk:**  
Clients may incorrectly assume that bulk creation is fully atomic, while the server might actually create some tasks and reject others. If the server returns 207 with partial failures, clients expecting a single 200 may not handle the mixed result correctly.
