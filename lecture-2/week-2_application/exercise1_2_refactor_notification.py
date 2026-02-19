from abc import ABC, abstractmethod

# ============================================================================
# ABSTRACTION
# ============================================================================
class EmailProvider(ABC):
    """
    The Interface: Defines WHAT an email provider must do.
    By depending on this ABC, the NotificationService doesn't care 
    which third-party service is actually sending the mail.
    """
    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        pass


class SendGridEmailProvider(EmailProvider):
    """
    Hides the complexity of API keys, URLs, and HTTP requests.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key 
        self.base_url = "https://api.sendgrid.com/v3/mail/send"

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        # Imagine actual 'requests.post' logic here
        print(f"Sending email to {recipient} via SendGrid with subject '{subject}'")
        return True
    
class MockEmailProvider(EmailProvider):
    """
    Allows us to run the entire system without sending real emails during testing.
    """
    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        print(f"Mock sending email to {recipient} with subject '{subject}'")
        return True

# ============================================================================
# Business Logic
# ============================================================================
class NotificationService:
    """
    
    REFACTORING HELPS US ACHIEVE:
    1. Single Responsibility: This class now only handles notification 
       workflows (logic/flow), not API management.
    2. Dependency Injection: We inject the provider via the constructor,
       making the service highly flexible and testable.
    """
    def __init__(self, email_provider: EmailProvider):
        # We store the abstraction, not a specific class
        self.email_provider = email_provider

    def send_notification(self, recipient: str, subject: str, body: str):
        # The service 'trusts' the contract defined in EmailProvider
        success = self.email_provider.send_email(
            recipient=recipient, 
            subject=subject, 
            body=body
        )
        if success:
            print("User notified successfully.")

# ============================================================================
# DEMONSTRATION
# ============================================================================
if __name__ == "__main__":
    # We use the real provider. If we switch a provider tomorrow,
    # we ONLY change this line.
    sendgrid_provider = SendGridEmailProvider(api_key="SG.xxx")
    service = NotificationService(email_provider=sendgrid_provider)
    service.send_notification("sonia@as.com", "Welcome!", "Thanks for signing up!")

    # We use the Mock provider. The NotificationService code remains 
    # exactly the same, but behaves differently.
    mock_provider = MockEmailProvider()
    test_service = NotificationService(email_provider=mock_provider)
    test_service.send_notification("test@as.com", "Test", "Testing 123...")