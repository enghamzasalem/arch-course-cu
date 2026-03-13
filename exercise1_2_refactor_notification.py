#!/usr/bin/env python3
"""
Exercise 1.2: Refactor Bad Code to Use Abstraction 🟡

This example demonstrates:
- How to identify tightly coupled, non-testable code
- Refactoring techniques to introduce abstraction
- Breaking vendor lock-in through interface design
- Testing without external dependencies

Business Scenario: Email Notification System
- Original: Hardcoded dependency on SendGrid (vendor lock-in)
- Refactored: Abstract interface with multiple implementations
- Benefits: Testability, flexibility, maintainability
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


# ============================================================================
# PART 1: THE PROBLEM - Tightly Coupled, Non-Testable Code
# ============================================================================
# This is the BAD code we need to refactor. It has multiple issues:
# 1. Hardcoded vendor dependency (SendGrid lock-in)
# 2. Cannot test without real API calls
# 3. Violates Single Responsibility Principle
# 4. No error handling abstraction
# 5. Configuration buried in code

"""
class NotificationService:
    def __init__(self):
        self.sendgrid_api_key = "SG.xxx"
        self.sendgrid_url = "https://api.sendgrid.com/v3"
    
    def send_email(self, to: str, subject: str, body: str):
        # Direct SendGrid API calls
        import requests
        response = requests.post(
            f"{self.sendgrid_url}/mail/send",
            headers={"Authorization": f"Bearer {self.sendgrid_api_key}"},
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "noreply@company.com"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}]
            }
        )
        return response.status_code == 202
"""


# ============================================================================
# PART 2: THE SOLUTION - Abstract Interface Design
# ============================================================================

@dataclass
class EmailMessage:
    """Standardized email message format"""
    to: str
    subject: str
    body: str
    from_email: str = "noreply@company.com"
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[Dict] = field(default_factory=list)
    is_html: bool = False


@dataclass
class EmailResult:
    """Standardized result from email providers"""
    success: bool
    message_id: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


# Abstract Interface - The Key to Flexibility
class EmailProvider(ABC):
    """
    Abstract interface for email providers.
    
    This is the architectural contract that all email providers must follow.
    Clients depend on this interface, not concrete implementations.
    """
    
    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send an email using the provider.
        
        Args:
            message: Standardized email message
            
        Returns:
            EmailResult with status and details
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass


# ============================================================================
# CONCRETE IMPLEMENTATION 1: SendGrid Provider (Wraps Legacy Code)
# ============================================================================

class SendGridEmailProvider(EmailProvider):
    """
    SendGrid implementation of EmailProvider.
    
    This wraps the original tightly-coupled code into a clean interface.
    All the SendGrid-specific complexity is hidden here.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.sendgrid.com/v3"):
        """
        Initialize SendGrid provider.
        
        Args:
            api_key: SendGrid API key (defaults to environment variable)
            api_url: SendGrid API URL
        """
        self.api_key = api_key or os.environ.get("SENDGRID_API_KEY", "SG.demo_key")
        self.api_url = api_url
        self._available = True
        print(f"  [SendGrid] Initialized with API URL: {api_url}")
    
    def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send email via SendGrid API.
        
        This contains all the original SendGrid-specific code,
        but now it's properly encapsulated.
        """
        try:
            print(f"  [SendGrid] Preparing email to: {message.to}")
            print(f"  [SendGrid] Subject: {message.subject}")
            
            # Simulate API call (in real code, this would be actual requests.post)
            # This is where the original tightly-coupled code lives
            success = self._call_sendgrid_api(message)
            
            if success:
                message_id = f"sg_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(message.to) % 10000}"
                print(f"  [SendGrid] ✅ Email sent! Message ID: {message_id}")
                return EmailResult(
                    success=True,
                    message_id=message_id,
                    provider=self.get_provider_name()
                )
            else:
                return EmailResult(
                    success=False,
                    provider=self.get_provider_name(),
                    error="SendGrid API returned error"
                )
                
        except Exception as e:
            print(f"  [SendGrid] ❌ Error: {str(e)}")
            return EmailResult(
                success=False,
                provider=self.get_provider_name(),
                error=str(e)
            )
    
    def _call_sendgrid_api(self, message: EmailMessage) -> bool:
        """
        Simulate SendGrid API call.
        
        In the original code, this was inline in the send_email method.
        Now it's properly encapsulated.
        """
        # This is where the actual requests.post would happen
        # We're simulating for demonstration
        print(f"  [SendGrid] POST {self.api_url}/mail/send")
        print(f"  [SendGrid] Headers: Authorization: Bearer {self.api_key[:5]}...")
        print(f"  [SendGrid] Body: SendGrid-specific JSON format")
        
        # Simulate successful API call 90% of the time
        import random
        return random.random() < 0.9
    
    def get_provider_name(self) -> str:
        return "SendGrid"
    
    def is_available(self) -> bool:
        # In real code, this might check API health endpoint
        return self._available


# ============================================================================
# CONCRETE IMPLEMENTATION 2: Mock Provider (For Testing)
# ============================================================================

class MockEmailProvider(EmailProvider):
    """
    Mock email provider for testing.
    
    This is a completely different implementation but same interface!
    No actual emails are sent, perfect for:
    - Unit tests
    - Development environments
    - CI/CD pipelines
    - Demo/training scenarios
    """
    
    def __init__(self, should_succeed: bool = True, fail_count: int = 0):
        """
        Initialize mock provider.
        
        Args:
            should_succeed: Whether emails should succeed by default
            fail_count: Number of failures to simulate before succeeding
        """
        self.should_succeed = should_succeed
        self.fail_count = fail_count
        self.current_fail_count = 0
        self.sent_emails: List[EmailMessage] = []  # For test verification
        self._available = True
        print(f"  [MockProvider] Initialized (should_succeed={should_succeed})")
    
    def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Mock sending email - no actual API calls!
        
        Records emails for test verification instead.
        """
        # Record email for test assertions
        self.sent_emails.append(message)
        
        print(f"  [MockProvider] 📧 Captured email to: {message.to}")
        print(f"  [MockProvider] Subject: {message.subject}")
        print(f"  [MockProvider] Body preview: {message.body[:50]}...")
        
        # Simulate failures if configured
        if not self.should_succeed:
            return EmailResult(
                success=False,
                provider=self.get_provider_name(),
                error="Mock provider configured to fail"
            )
        
        if self.current_fail_count < self.fail_count:
            self.current_fail_count += 1
            return EmailResult(
                success=False,
                provider=self.get_provider_name(),
                error=f"Simulated failure #{self.current_fail_count}"
            )
        
        # Success case
        return EmailResult(
            success=True,
            message_id=f"mock_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            provider=self.get_provider_name()
        )
    
    def get_provider_name(self) -> str:
        return "MockProvider"
    
    def is_available(self) -> bool:
        return self._available
    
    # Test helper methods
    def get_sent_emails_count(self) -> int:
        """Get number of emails sent (for test assertions)"""
        return len(self.sent_emails)
    
    def get_last_email(self) -> Optional[EmailMessage]:
        """Get the last sent email (for test assertions)"""
        return self.sent_emails[-1] if self.sent_emails else None
    
    def clear_sent_emails(self):
        """Clear sent emails history"""
        self.sent_emails.clear()


# ============================================================================
# CONCRETE IMPLEMENTATION 3: Console Provider (For Development)
# ============================================================================

class ConsoleEmailProvider(EmailProvider):
    """
    Console email provider - prints to console instead of sending.
    
    Useful for:
    - Development environments
    - Debugging
    - Demonstration purposes
    """
    
    def __init__(self, pretty_print: bool = True):
        self.pretty_print = pretty_print
        self._available = True
        print(f"  [ConsoleProvider] Initialized (pretty_print={pretty_print})")
    
    def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Print email to console instead of sending.
        """
        print("\n" + "=" * 60)
        print("📨 CONSOLE EMAIL OUTPUT")
        print("=" * 60)
        print(f"To:      {message.to}")
        print(f"From:    {message.from_email}")
        print(f"Subject: {message.subject}")
        if message.cc:
            print(f"CC:      {', '.join(message.cc)}")
        if message.bcc:
            print(f"BCC:     {', '.join(message.bcc)}")
        print("-" * 60)
        print(f"Body:\n{message.body}")
        print("=" * 60 + "\n")
        
        return EmailResult(
            success=True,
            message_id=f"console_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            provider=self.get_provider_name()
        )
    
    def get_provider_name(self) -> str:
        return "ConsoleProvider"
    
    def is_available(self) -> bool:
        return self._available


# ============================================================================
# REFACTORED CLIENT CODE: Notification Service
# ============================================================================

class NotificationService:
    """
    Refactored notification service that depends on abstraction.
    
    Key improvements:
    1. No hardcoded vendor dependencies
    2. Testable with mock implementations
    3. Configurable at runtime
    4. Follows Dependency Injection pattern
    5. Single Responsibility Principle
    """
    
    def __init__(self, email_provider: EmailProvider):
        """
        Dependency Injection: Provider is injected, not hardcoded.
        
        This is the heart of the refactoring - we now depend on
        the interface, not a concrete implementation.
        """
        self.email_provider = email_provider
        print(f"  [NotificationService] Initialized with {email_provider.get_provider_name()}")
    
    def send_notification(self, user_email: str, subject: str, message: str) -> EmailResult:
        """
        Send a notification email.
        
        This method doesn't know or care which provider is being used!
        """
        print(f"\n📧 Sending notification to: {user_email}")
        
        # Create standardized email message
        email = EmailMessage(
            to=user_email,
            subject=f"Notification: {subject}",
            body=message,
            from_email="notifications@company.com"
        )
        
        # Send using injected provider
        result = self.email_provider.send_email(email)
        
        if result.success:
            print(f"  ✅ Notification sent via {result.provider}")
            print(f"  📎 Message ID: {result.message_id}")
        else:
            print(f"  ❌ Failed to send notification: {result.error}")
        
        return result
    
    def send_welcome_email(self, user_email: str, user_name: str) -> EmailResult:
        """Send a welcome email to new users"""
        subject = "Welcome to Our Platform!"
        body = f"""
        Hello {user_name},
        
        Welcome to our platform! We're excited to have you on board.
        
        Best regards,
        The Team
        """
        return self.send_notification(user_email, subject, body)
    
    def send_password_reset(self, user_email: str, reset_token: str) -> EmailResult:
        """Send password reset email"""
        subject = "Password Reset Request"
        body = f"""
        You requested a password reset.
        
        Your reset token is: {reset_token}
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The Team
        """
        return self.send_notification(user_email, subject, body)


# ============================================================================
# BEFORE/AFTER COMPARISON DEMONSTRATION
# ============================================================================

def demonstrate_before_after():
    """Show the transformation from tightly-coupled to abstract code"""
    
    print("=" * 80)
    print("BEFORE REFACTORING: Tightly Coupled Code")
    print("=" * 80)
    print("""
    class NotificationService:
        def __init__(self):
            # ❌ Hardcoded vendor configuration
            self.sendgrid_api_key = "SG.xxx"
            self.sendgrid_url = "https://api.sendgrid.com/v3"
        
        def send_email(self, to, subject, body):
            # ❌ Direct vendor API dependency
            import requests
            response = requests.post(
                f"{self.sendgrid_url}/mail/send",
                headers={"Authorization": f"Bearer {self.sendgrid_api_key}"},
                json={...}  # ❌ SendGrid-specific format
            )
            return response.status_code == 202
        
        # ❌ Cannot test without real API calls
        # ❌ Cannot switch to different provider
        # ❌ Violates Single Responsibility
    """)
    
    print("\n" + "=" * 80)
    print("AFTER REFACTORING: Abstract Interface Design")
    print("=" * 80)
    print("""
    # ✅ Clean abstraction
    class EmailProvider(ABC):
        @abstractmethod
        def send_email(self, message: EmailMessage) -> EmailResult:
            pass
    
    # ✅ Vendor-specific code encapsulated
    class SendGridEmailProvider(EmailProvider):
        def send_email(self, message):
            # All SendGrid complexity isolated here
    
    # ✅ Test implementation
    class MockEmailProvider(EmailProvider):
        def send_email(self, message):
            # No API calls, records emails for testing
    
    # ✅ Client depends on abstraction
    class NotificationService:
        def __init__(self, email_provider: EmailProvider):
            self.email_provider = email_provider  # ✅ Dependency injection
        
        def send_notification(self, user_email, subject, message):
            # ✅ Works with ANY email provider
            return self.email_provider.send_email(...)
    """)


# ============================================================================
# TEST DEMONSTRATION - Testing Without Real API Calls
# ============================================================================

def demonstrate_testability():
    """Show how abstraction enables proper testing"""
    
    print("\n" + "=" * 80)
    print("TESTING DEMONSTRATION: No Real API Calls!")
    print("=" * 80)
    
    # Create mock provider for testing
    print("\n📊 TEST SCENARIO 1: Successful Email")
    mock_provider = MockEmailProvider(should_succeed=True)
    service = NotificationService(mock_provider)
    
    # Send test email
    result = service.send_welcome_email("test@example.com", "Test User")
    
    # Verify results without any real API calls
    assert result.success == True
    assert result.provider == "MockProvider"
    assert mock_provider.get_sent_emails_count() == 1
    
    last_email = mock_provider.get_last_email()
    assert last_email.to == "test@example.com"
    assert "Welcome" in last_email.subject
    
    print(f"\n✅ Test passed: Email was recorded, not actually sent")
    print(f"   Emails sent: {mock_provider.get_sent_emails_count()}")
    print(f"   Last email to: {last_email.to}")
    
    print("\n📊 TEST SCENARIO 2: Simulated Failure")
    mock_provider = MockEmailProvider(should_succeed=False)
    service = NotificationService(mock_provider)
    
    result = service.send_password_reset("fail@example.com", "TOKEN123")
    
    assert result.success == False
    assert result.error is not None
    
    print(f"\n✅ Test passed: Failure handled gracefully")
    print(f"   Error: {result.error}")
    
    print("\n📊 TEST SCENARIO 3: Retry Logic Test")
    mock_provider = MockEmailProvider(should_succeed=True, fail_count=2)
    service = NotificationService(mock_provider)
    
    # First attempt - should fail
    result1 = service.send_notification("retry@example.com", "Test", "Message 1")
    # Second attempt - should fail
    result2 = service.send_notification("retry@example.com", "Test", "Message 2")
    # Third attempt - should succeed
    result3 = service.send_notification("retry@example.com", "Test", "Message 3")
    
    print(f"   Attempt 1: {'✅' if result1.success else '❌'} - {result1.error}")
    print(f"   Attempt 2: {'✅' if result2.success else '❌'} - {result2.error}")
    print(f"   Attempt 3: {'✅' if result3.success else '❌'} - Message ID: {result3.message_id}")
    
    print("\n🎯 KEY INSIGHT: We tested thoroughly WITHOUT:")
    print("   • Real SendGrid API keys")
    print("   • Network connectivity")
    print("   • External service dependencies")
    print("   • Risk of sending test emails to real addresses")


# ============================================================================
# PRODUCTION VS DEVELOPMENT DEMONSTRATION
# ============================================================================

def demonstrate_environment_switching():
    """Show how different environments can use different providers"""
    
    print("\n" + "=" * 80)
    print("ENVIRONMENT CONFIGURATION DEMONSTRATION")
    print("=" * 80)
    
    # Development environment - Use console provider
    print("\n🛠️  DEVELOPMENT ENVIRONMENT:")
    dev_provider = ConsoleEmailProvider(pretty_print=True)
    dev_service = NotificationService(dev_provider)
    dev_service.send_welcome_email("dev@localhost", "Dev User")
    
    # Testing environment - Use mock provider
    print("\n🧪 TESTING ENVIRONMENT:")
    test_provider = MockEmailProvider(should_succeed=True)
    test_service = NotificationService(test_provider)
    test_service.send_password_reset("test@example.com", "RESET123")
    print(f"   Test assertions passed: {test_provider.get_sent_emails_count()} email recorded")
    
    # Production environment - Use real SendGrid
    print("\n🚀 PRODUCTION ENVIRONMENT:")
    prod_provider = SendGridEmailProvider(api_key="SG.production_key_123")
    prod_service = NotificationService(prod_provider)
    prod_service.send_welcome_email("customer@realcompany.com", "Real Customer")
    
    print("\n🎯 KEY INSIGHT: Same code, different configurations!")
    print("   • Development: Console output (no emails sent)")
    print("   • Testing: Mock provider (verification only)")
    print("   • Production: Real SendGrid (actual emails)")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Main demonstration of the refactored code"""
    
    print("=" * 80)
    print("EXERCISE 1.2: Refactor Bad Code to Use Abstraction")
    print("=" * 80)
    
    # Show before/after comparison
    demonstrate_before_after()
    
    # Demonstrate testability
    demonstrate_testability()
    
    # Demonstrate environment switching
    demonstrate_environment_switching()
    
    print("\n" + "=" * 80)
    print("SUMMARY OF IMPROVEMENTS")
    print("=" * 80)
    print("""
    ❌ BEFORE (Tightly Coupled):
    • Hardcoded SendGrid dependency → Vendor lock-in
    • Cannot test without API calls → Slow, brittle tests
    • Configuration buried in code → Not configurable
    • Mixed responsibilities → Hard to maintain
    • No error handling abstraction → Inconsistent error handling
    
    ✅ AFTER (Abstract Interface):
    • Clean EmailProvider interface → No vendor lock-in
    • Mock provider for testing → Fast, reliable tests
    • Dependency injection → Configurable at runtime
    • Single responsibility → Easy to maintain
    • Standardized EmailResult → Consistent error handling
    
    🎯 KEY ARCHITECTURAL WIN:
    We can now add new providers (AWS SES, Mailgun, SMTP) 
    WITHOUT changing the NotificationService code!
    """)


if __name__ == "__main__":
    main()
