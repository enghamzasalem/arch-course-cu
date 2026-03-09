#!/usr/bin/env python3
"""
Example 1: Modularity and Separation of Concerns

This example demonstrates:
- Principles of Modularity: Decompose into independent, well-defined units
- Separation of Concerns: Each module handles one concern
- Single Responsibility Principle (SRP): One reason to change
- Component boundaries and independence

Key Concept: Modularity means building systems from independent components
that can be developed, tested, and maintained separately.

Reference: Chapter 5 - Modularity and Components
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================================
# BUSINESS SCENARIO: Order Processing System
# ============================================================================
# BAD: Monolithic OrderProcessor doing everything
# GOOD: Modular components - OrderValidator, InventoryChecker, PaymentProcessor, OrderPersister


# ============================================================================
# BAD: MONOLITHIC (Low Modularity)
# ============================================================================

class MonolithicOrderProcessor:
    """
    ANTI-PATTERN: Everything in one class
    - Violates Single Responsibility
    - Hard to test
    - Hard to change one concern without affecting others
    """
    
    def process_order(self, order: Dict) -> Dict:
        """Does validation, inventory, payment, persistence, notification - all mixed!"""
        # Concern 1: Validation (should be separate)
        if not order.get("items"):
            return {"error": "No items"}
        if not order.get("customer_id"):
            return {"error": "No customer"}
        
        # Concern 2: Inventory (should be separate)
        for item in order["items"]:
            # Fake inventory check - mixed with order logic
            if item.get("quantity", 0) > 100:
                return {"error": "Insufficient stock"}
        
        # Concern 3: Payment (should be separate)
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in order["items"])
        # Fake payment - mixed with order logic
        if total > 10000:
            return {"error": "Payment declined"}
        
        # Concern 4: Persistence (should be separate)
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Concern 5: Notification (should be separate)
        # Fake notification - mixed with order logic
        print(f"[Monolithic] Would send confirmation to customer {order.get('customer_id')}")
        
        return {"order_id": order_id, "status": "completed", "total": total}


# ============================================================================
# GOOD: MODULAR (High Modularity)
# ============================================================================

@dataclass
class Order:
    """Order data structure"""
    customer_id: str
    items: List[Dict]
    total: float = 0.0
    order_id: Optional[str] = None


# --- Component 1: Validation (Single Responsibility) ---

class OrderValidator:
    """
    SRP: Validates order structure and business rules only.
    One reason to change: validation rules change.
    """
    
    def validate(self, order_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate order. Returns (is_valid, error_message)."""
        if not order_data.get("items"):
            return False, "No items in order"
        if not order_data.get("customer_id"):
            return False, "Customer ID required"
        for item in order_data["items"]:
            if not item.get("product_id") or item.get("quantity", 0) <= 0:
                return False, f"Invalid item: {item}"
        return True, None


# --- Component 2: Inventory (Single Responsibility) ---

class InventoryChecker:
    """
    SRP: Checks inventory availability only.
    One reason to change: inventory system or rules change.
    """
    
    def __init__(self, stock: Optional[Dict[str, int]] = None):
        self._stock = stock or {"prod-1": 50, "prod-2": 30, "prod-3": 100}
    
    def check_availability(self, items: List[Dict]) -> Tuple[bool, Optional[str]]:
        """Check if all items are in stock."""
        for item in items:
            product_id = item.get("product_id", "")
            needed = item.get("quantity", 0)
            available = self._stock.get(product_id, 0)
            if needed > available:
                return False, f"Insufficient stock for {product_id}"
        return True, None


# --- Component 3: Payment (Single Responsibility) ---

class PaymentProcessor:
    """
    SRP: Processes payments only.
    One reason to change: payment provider or rules change.
    """
    
    def process(self, amount: float, customer_id: str) -> Tuple[bool, Optional[str]]:
        """Process payment. Returns (success, error_message)."""
        if amount <= 0:
            return False, "Invalid amount"
        if amount > 10000:
            return False, "Payment limit exceeded"
        # Simulate payment
        return True, None


# --- Component 4: Persistence (Single Responsibility) ---

class OrderRepository:
    """
    SRP: Persists and retrieves orders only.
    One reason to change: storage mechanism changes.
    """
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def save(self, order: Order) -> str:
        """Save order and return order_id."""
        order_id = order.order_id or f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order.order_id = order_id
        self._orders[order_id] = order
        return order_id
    
    def get(self, order_id: str) -> Optional[Order]:
        """Retrieve order by ID."""
        return self._orders.get(order_id)


# --- Component 5: Notification (Single Responsibility) ---

class OrderNotifier:
    """
    SRP: Sends order notifications only.
    One reason to change: notification channel or format changes.
    """
    
    def send_confirmation(self, order_id: str, customer_id: str) -> None:
        """Send order confirmation to customer."""
        print(f"[OrderNotifier] Confirmation sent: order {order_id} to customer {customer_id}")


# --- Orchestrator: Composes components (Separation of orchestration) ---

class ModularOrderProcessor:
    """
    Composes modular components.
    SRP: Orchestrates order processing flow only.
    Each component can be tested, replaced, or modified independently.
    """
    
    def __init__(
        self,
        validator: OrderValidator,
        inventory: InventoryChecker,
        payment: PaymentProcessor,
        repository: OrderRepository,
        notifier: OrderNotifier,
    ):
        self.validator = validator
        self.inventory = inventory
        self.payment = payment
        self.repository = repository
        self.notifier = notifier
    
    def process_order(self, order_data: Dict) -> Dict:
        """Process order using modular components."""
        # 1. Validate
        valid, error = self.validator.validate(order_data)
        if not valid:
            return {"error": error}
        
        # 2. Check inventory
        available, error = self.inventory.check_availability(order_data["items"])
        if not available:
            return {"error": error}
        
        # 3. Calculate total
        total = sum(
            item.get("price", 0) * item.get("quantity", 1)
            for item in order_data["items"]
        )
        
        # 4. Process payment
        success, error = self.payment.process(total, order_data["customer_id"])
        if not success:
            return {"error": error}
        
        # 5. Create and persist order
        order = Order(
            customer_id=order_data["customer_id"],
            items=order_data["items"],
            total=total,
        )
        order_id = self.repository.save(order)
        
        # 6. Send notification
        self.notifier.send_confirmation(order_id, order_data["customer_id"])
        
        return {"order_id": order_id, "status": "completed", "total": total}


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_modularity():
    """Compare monolithic vs modular approach."""
    
    print("\n" + "="*70)
    print("MODULARITY: Monolithic vs Modular Order Processing")
    print("="*70)
    
    order_data = {
        "customer_id": "cust-001",
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 25.0},
            {"product_id": "prod-2", "quantity": 1, "price": 50.0},
        ],
    }
    
    # Monolithic
    print("\n--- MONOLITHIC (Single class, mixed concerns) ---")
    monolithic = MonolithicOrderProcessor()
    result = monolithic.process_order(order_data)
    print(f"Result: {result}")
    
    # Modular
    print("\n--- MODULAR (Separate components, clear responsibilities) ---")
    modular = ModularOrderProcessor(
        validator=OrderValidator(),
        inventory=InventoryChecker(),
        payment=PaymentProcessor(),
        repository=OrderRepository(),
        notifier=OrderNotifier(),
    )
    result = modular.process_order(order_data)
    print(f"Result: {result}")
    
    print("\n" + "="*70)
    print("KEY CONCEPTS")
    print("="*70)
    print("""
MODULARITY PRINCIPLES:
  • Decompose: Break system into independent units
  • Encapsulate: Hide implementation, expose interface
  • Compose: Build system from modules

SEPARATION OF CONCERNS:
  • Each component handles ONE concern
  • Validation ≠ Inventory ≠ Payment ≠ Persistence ≠ Notification
  • Change one without affecting others

SINGLE RESPONSIBILITY PRINCIPLE (SRP):
  • One reason to change per component
  • OrderValidator: validation rules change
  • PaymentProcessor: payment provider changes
  • Easier to test, maintain, reuse

BENEFITS:
  • Test each component in isolation (mock others)
  • Replace components (e.g., different payment provider)
  • Parallel development by different developers
  • Clear boundaries and dependencies
    """)


if __name__ == "__main__":
    demonstrate_modularity()
