# Exercise 1.2 — Refactor NotificationService to Use Abstraction

Summary
- Introduced an `EmailProvider` abstract interface.
- Implemented `SendGridEmailProvider` (thin wrapper / simulated) and `MockEmailProvider` for tests.
- Refactored `NotificationService` to accept an `EmailProvider` via dependency injection.

Before
- `NotificationService` directly constructed and called SendGrid-specific code, making testing and provider substitution hard.

After
- `NotificationService` depends on `EmailProvider`. You can inject `MockEmailProvider` during tests.

Improvements
- Testability: unit tests can run without network calls.
- Flexibility: swap providers (SMTP, SES, other) without changing business logic.
- Reduced vendor lock-in: provider-specific code isolated behind the interface.

Usage
- Run the demo: `python solutions/exercise1_2_refactor_notification.py`
