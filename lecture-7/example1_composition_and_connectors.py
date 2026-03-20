#!/usr/bin/env python3
"""
Example 1: Component Composition and Connector Types

This example demonstrates:
- Component Composition: building systems from smaller components
- Connector Types: synchronous (RPC, direct call) vs asynchronous (message queue)
- Message Passing: request/response and fire-and-forget
- Service Composition: composing services into a workflow

Key Concept: Composition = assembling components; Connectors = how they communicate.

Reference: Chapter 7 - Composability and Connectors
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time


# ============================================================================
# BUSINESS SCENARIO: Order Processing Pipeline
# ============================================================================
# Components: InventoryService, PaymentService, ShippingService, Notifier
# Connectors: sync (direct call) for payment check, async (queue) for shipping/notify


# ============================================================================
# CONNECTOR TYPES
# ============================================================================

class ConnectorType(Enum):
    """Types of connectors between components"""
    DIRECT_CALL = "direct_call"       # Sync, same process
    RPC = "rpc"                       # Sync, cross-process
    MESSAGE_QUEUE = "message_queue"   # Async, decoupled
    EVENT_BUS = "event_bus"           # Async, pub/sub
    REST_HTTP = "rest_http"           # Sync, HTTP request/response


@dataclass
class Connector:
    """Represents a connector between two components"""
    name: str
    connector_type: ConnectorType
    source: str
    target: str
    protocol: str
    is_async: bool
    
    def describe(self) -> str:
        sync = "async" if self.is_async else "sync"
        return f"{self.source} --[{self.name}, {sync}]--> {self.target}"


# ============================================================================
# COMPONENTS (Services)
# ============================================================================

class InventoryService:
    """Component: checks and reserves inventory."""
    
    def __init__(self) -> None:
        self._stock: Dict[str, int] = {"item-A": 10, "item-B": 5}
    
    def check_and_reserve(self, item_id: str, quantity: int) -> bool:
        if self._stock.get(item_id, 0) >= quantity:
            self._stock[item_id] -= quantity
            return True
        return False


class PaymentService:
    """Component: processes payments."""
    
    def charge(self, order_id: str, amount: float) -> bool:
        # Simulate payment
        return amount > 0 and amount < 100_000


class ShippingService:
    """Component: creates shipping label (simulated async)."""
    
    def create_shipment(self, order_id: str, address: str) -> str:
        return f"SHIP-{order_id}-001"


class Notifier:
    """Component: sends notifications (simulated async)."""
    
    def send(self, recipient: str, message: str) -> None:
        print(f"  [Notifier] → {recipient}: {message}")


# ============================================================================
# COMPOSITION: Order Processor composes services via connectors
# ============================================================================

class OrderProcessor:
    """
    Composes Inventory, Payment, Shipping, Notifier.
    Uses different connector types:
    - Sync direct call: inventory, payment (need immediate result)
    - Async / fire-and-forget: shipping, notify (can be queued)
    """
    
    def __init__(
        self,
        inventory: InventoryService,
        payment: PaymentService,
        shipping: ShippingService,
        notifier: Notifier,
    ) -> None:
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping
        self.notifier = notifier
        self._connectors: List[Connector] = [
            Connector("check_stock", ConnectorType.DIRECT_CALL, "OrderProcessor", "InventoryService", "method call", False),
            Connector("charge", ConnectorType.DIRECT_CALL, "OrderProcessor", "PaymentService", "method call", False),
            Connector("ship", ConnectorType.MESSAGE_QUEUE, "OrderProcessor", "ShippingService", "async message", True),
            Connector("notify", ConnectorType.MESSAGE_QUEUE, "OrderProcessor", "Notifier", "async message", True),
        ]
    
    def process_order(self, order_id: str, items: List[Dict], total: float, email: str, address: str) -> Dict[str, Any]:
        # Sync: inventory
        for item in items:
            if not self.inventory.check_and_reserve(item["id"], item.get("qty", 1)):
                return {"success": False, "error": "insufficient stock"}
        
        # Sync: payment
        if not self.payment.charge(order_id, total):
            return {"success": False, "error": "payment failed"}
        
        # Async (simulated): shipping – in real system would enqueue
        shipment_id = self.shipping.create_shipment(order_id, address)
        
        # Async (simulated): notify
        self.notifier.send(email, f"Order {order_id} confirmed. Shipment: {shipment_id}")
        
        return {"success": True, "order_id": order_id, "shipment_id": shipment_id}
    
    def get_connectors(self) -> List[Connector]:
        return self._connectors


# ============================================================================
# MESSAGE PASSING PATTERNS
# ============================================================================

@dataclass
class Message:
    """Generic message for connector."""
    type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None


class MessageQueueConnector:
    """Simulates async message queue connector."""
    
    def __init__(self) -> None:
        self._queue: List[Message] = []
    
    def send(self, msg: Message) -> None:
        self._queue.append(msg)
        print(f"  [Queue] enqueued: {msg.type}")
    
    def receive(self) -> Optional[Message]:
        return self._queue.pop(0) if self._queue else None


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_composition() -> None:
    print("\n" + "="*70)
    print("COMPOSITION: Order Processor = Inventory + Payment + Shipping + Notifier")
    print("="*70)
    
    processor = OrderProcessor(
        inventory=InventoryService(),
        payment=PaymentService(),
        shipping=ShippingService(),
        notifier=Notifier(),
    )
    
    result = processor.process_order(
        order_id="ORD-001",
        items=[{"id": "item-A", "qty": 2}],
        total=99.99,
        email="user@example.com",
        address="123 Main St",
    )
    
    print("\nResult:", result)
    
    print("\nConnectors used:")
    for c in processor.get_connectors():
        print(" ", c.describe())
    
    print("\n" + "="*70)
    print("KEY CONCEPTS")
    print("="*70)
    print("""
COMPOSITION:
  • System = set of components + connectors
  • OrderProcessor composes four services; it does not implement their logic
  • Each component has a single responsibility

CONNECTOR TYPES:
  • Direct call (sync): when you need immediate result (inventory, payment)
  • Message queue (async): when you can defer (shipping, notification)
  • Choice depends on: latency, coupling, failure isolation

MESSAGE PASSING:
  • Sync: request → wait → response
  • Async: send message → continue; consumer processes later
  • Async improves responsiveness and decouples components
    """)


if __name__ == "__main__":
    demonstrate_composition()
