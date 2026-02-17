#!/usr/bin/env python3
"""
BAD EXAMPLE 1: No Internal Quality - Spaghetti Code

This demonstrates what happens when you DON'T focus on internal quality.
Compare this to example1_internal_vs_external_quality.py to see the difference.

PROBLEMS:
1. No code organization - everything in one file
2. No documentation - unreadable code
3. No tests - bugs everywhere
4. High complexity - impossible to understand
5. Technical debt accumulates rapidly
"""

from typing import Dict, List, Optional
import time
import random


# ============================================================================
# BAD: No internal quality - spaghetti code
# ============================================================================

class ECommerceSystem:
    """
    BAD ARCHITECTURE: No internal quality
    
    Problems:
    - Everything in one class
    - No separation of concerns
    - No documentation
    - High complexity
    - No tests
    - Technical debt everywhere
    """
    
    def __init__(self):
        # Global state - everything mixed together
        self.users = {}
        self.products = {}
        self.orders = {}
        self.payments = {}
        self.inventory = {}
        self.cart = {}
        self.shipping = {}
        self.notifications = {}
        self.analytics = {}
        self.config = {}
        self.cache = {}
        self.db = {}
        self.api_keys = {}
        self.logs = []
        self.errors = []
        self.metrics = {}
        # ... and 50 more global variables
        self.bug_count = 0
        self.technical_debt = 0.0
    
    def process_order(self, user_id, product_ids, payment_info, shipping_info):
        """
        BAD: One massive function that does everything
        - 500+ lines of code
        - Handles user, product, order, payment, shipping, inventory, notifications
        - Impossible to test
        - Impossible to understand
        - Impossible to maintain
        """
        print(f"\n🛒 Processing order for user {user_id}")
        
        # Check user (but what if user doesn't exist? who knows!)
        if user_id not in self.users:
            # Create user on the fly? Maybe? Who knows what this does!
            self.users[user_id] = {"id": user_id, "orders": []}
        
        # Validate products (but validation is incomplete)
        total = 0
        for pid in product_ids:
            if pid in self.products:
                # What if product is out of stock? Not checked!
                price = self.products[pid].get("price", 0)  # Might be None!
                total += price
            else:
                # Product doesn't exist? Just skip it? Or error? Who knows!
                print(f"   ⚠️  Product {pid} not found (but continuing anyway)")
        
        # Process payment (but error handling is terrible)
        try:
            # Direct API call - no abstraction!
            payment_result = self._call_payment_api_directly(payment_info, total)
            if payment_result.get("success"):
                # Create order (but what if this fails?)
                order_id = f"order_{random.randint(1000, 9999)}"
                self.orders[order_id] = {
                    "id": order_id,
                    "user_id": user_id,
                    "products": product_ids,
                    "total": total,
                    "status": "pending"  # But status might never update!
                }
                
                # Update inventory (but what if this fails? Order created but inventory wrong!)
                for pid in product_ids:
                    if pid in self.inventory:
                        self.inventory[pid] = self.inventory[pid] - 1  # Might go negative!
                
                # Send notification (but what if this fails? User never knows!)
                self._send_notification_unsafely(user_id, f"Order {order_id} created")
                
                # Update analytics (but what if this fails? Data is wrong!)
                self._update_analytics_unsafely(order_id)
                
                # Log something (but logs are inconsistent)
                self.logs.append(f"Order {order_id} created")
                
                return {"success": True, "order_id": order_id}
            else:
                # Payment failed - but order might have been partially created!
                return {"success": False, "error": "Payment failed"}
        except Exception as e:
            # Catch all exceptions - hide all errors!
            print(f"   ❌ Error: {str(e)} (but continuing anyway)")
            self.errors.append(str(e))
            self.bug_count += 1
            return {"success": False, "error": "Unknown error"}
    
    def _call_payment_api_directly(self, payment_info, amount):
        """
        BAD: Direct API call - no abstraction, no error handling
        """
        # Simulate API call
        time.sleep(0.1)
        # What if API is down? What if network fails? Who knows!
        return {"success": random.random() > 0.1}  # 10% failure rate
    
    def _send_notification_unsafely(self, user_id, message):
        """
        BAD: No error handling, might fail silently
        """
        # What if notification service is down? User never gets notified!
        self.notifications[user_id] = message
        print(f"   📧 Notification sent (maybe)")
    
    def _update_analytics_unsafely(self, order_id):
        """
        BAD: No error handling, data might be wrong
        """
        # What if analytics service is down? Data is incomplete!
        self.analytics[order_id] = {"timestamp": time.time()}
    
    def get_bug_report(self):
        """Get bug report - but bugs are everywhere!"""
        return {
            "bugs": self.bug_count,
            "technical_debt": f"{self.technical_debt} hours",
            "code_complexity": "Very High (unmeasurable)",
            "test_coverage": "0% (no tests!)",
            "maintainability": "Impossible"
        }


# ============================================================================
# DEMONSTRATION: Why This Is Bad
# ============================================================================

def demonstrate_bad_internal_quality():
    """
    Demonstrate the problems with no internal quality
    """
    print("=" * 70)
    print("BAD EXAMPLE 1: No Internal Quality - Spaghetti Code")
    print("=" * 70)
    print("\n❌ PROBLEMS WITH THIS ARCHITECTURE:")
    print("   1. No code organization - everything in one class")
    print("   2. No documentation - code is unreadable")
    print("   3. No tests - bugs everywhere")
    print("   4. High complexity - impossible to understand")
    print("   5. Technical debt accumulates rapidly")
    print("   6. No error handling - failures are hidden")
    print("   7. No separation of concerns - everything mixed")
    
    system = ECommerceSystem()
    
    # Initialize some data (but initialization is inconsistent)
    system.products["prod1"] = {"price": 10.0}
    system.products["prod2"] = {"price": 20.0}
    system.inventory["prod1"] = 5
    system.inventory["prod2"] = 3
    
    print("\n" + "=" * 70)
    print("SCENARIO: Processing Orders")
    print("=" * 70)
    
    # Try to process orders
    for i in range(5):
        result = system.process_order(
            user_id=f"user_{i}",
            product_ids=["prod1", "prod2"],
            payment_info={"card": "1234"},
            shipping_info={"address": "123 Main St"}
        )
        if result.get("success"):
            print(f"   ✅ Order {result['order_id']} processed")
        else:
            print(f"   ❌ Order failed: {result.get('error')}")
    
    print("\n" + "=" * 70)
    print("BUG REPORT")
    print("=" * 70)
    report = system.get_bug_report()
    for key, value in report.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    print("SCENARIO: Developer Tries to Add Feature")
    print("=" * 70)
    print("""
    Developer wants to add "order cancellation" feature.
    
    With this architecture:
    1. Must find the right place in 500+ line function
    2. Must understand all the side effects
    3. Must test manually (no automated tests)
    4. Might break existing functionality
    5. Takes 2 weeks instead of 2 days
    
    Result: Feature takes 10x longer, introduces bugs, increases debt!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: Bug Report from User")
    print("=" * 70)
    print("""
    User reports: "I was charged but didn't receive my order"
    
    With this architecture:
    1. No logs to trace what happened
    2. No tests to reproduce the issue
    3. Code is too complex to understand
    4. Can't find where the bug is
    5. Fix might break other things
    
    Result: Bug takes weeks to fix, might not even fix it correctly!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: New Developer Joins Team")
    print("=" * 70)
    print("""
    New developer tries to understand the codebase.
    
    With this architecture:
    1. No documentation
    2. Code is unreadable
    3. No tests to understand behavior
    4. Everything is interconnected
    5. Can't make changes safely
    
    Result: Developer is unproductive for months, makes mistakes!
    """)
    
    print("\n" + "=" * 70)
    print("COMPARE TO: Good Architecture (example1_internal_vs_external_quality.py)")
    print("=" * 70)
    print("""
    With good internal quality:
    
    ✅ Modular code: Easy to understand
    ✅ Documentation: Code is self-documenting
    ✅ Tests: Can verify behavior
    ✅ Low complexity: Easy to reason about
    ✅ Error handling: Failures are handled gracefully
    ✅ Separation of concerns: Each module has one job
    
    See example1_internal_vs_external_quality.py for the solution!
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD IMPACT")
    print("=" * 70)
    print("""
    Company with poor internal quality:
    
    • Development speed: 5x slower
    • Bug rate: 10x higher
    • Developer satisfaction: 35% (vs 85% with good quality)
    • Technical debt: 500 hours (vs 20 hours)
    • Time to add feature: 2 weeks (vs 2 days)
    • Cost: $500k+ in lost productivity per year
    
    After 2 years:
    • Can't add new features
    • Must rewrite entire system
    • Lost competitive advantage
    • Team burnout and turnover
    """)


if __name__ == "__main__":
    demonstrate_bad_internal_quality()

