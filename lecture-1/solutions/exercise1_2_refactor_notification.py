from __future__ import annotations
import abc
from typing import Protocol, List


class EmailProvider(abc.ABC):
    @abc.abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool:
        """Send an email. Returns True on success."""


class SendGridEmailProvider(EmailProvider):
    def __init__(self, api_key: str, send_func=None):
        # `send_func` can be injected for testing to avoid real HTTP calls.
        self.api_key = api_key
        self._send = send_func

    def send(self, to: str, subject: str, body: str) -> bool:
        # Minimal wrapper that would call SendGrid. Here we simulate behavior
        if not self.api_key or self.api_key.startswith("SG."):
            # In a real implementation we'd make an HTTP request here.
            # If a custom send function is provided (for tests), use it.
            if self._send:
                return self._send(to=to, subject=subject, body=body)
            # Simulate success when API key looks valid (demo only)
            return True
        return False


class MockEmailProvider(EmailProvider):
    def __init__(self):
        self.sent: List[dict] = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append({"to": to, "subject": subject, "body": body})
        return True


class NotificationService:
    def __init__(self, email_provider: EmailProvider):
        self.email_provider = email_provider

    def notify_user(self, email: str, subject: str, body: str) -> bool:
        # Business logic could be added here (templating, retries, metrics)
        return self.email_provider.send(email, subject, body)


def _before_example():
    # Example of tightly-coupled code (conceptual) — not executed
    code = '''
class NotificationService:
    def __init__(self):
        self.sendgrid_api_key = "SG.xxx"
    def send_email(self, to, subject, body):
        # direct SendGrid call
        pass
'''
    return code


def _demo():
    # Using Mock provider for tests
    mock = MockEmailProvider()
    svc = NotificationService(mock)
    ok = svc.notify_user("alice@example.com", "Welcome", "Hello Alice")
    assert ok
    assert len(mock.sent) == 1

    # Swap to SendGrid provider without changing NotificationService
    sg = SendGridEmailProvider(api_key="SG.demo")
    svc2 = NotificationService(sg)
    assert svc2.notify_user("bob@example.com", "Hi", "Hi Bob")


if __name__ == "__main__":
    _demo()
    print("Exercise 1.2 demo passed (Mock + SendGrid wrapper)")
