#!/usr/bin/env python3
"""
Example 2: Orchestration vs Choreography and Event-Driven Composition

This example demonstrates:
- Orchestration: one central component coordinates others (directs the flow)
- Choreography: components react to events; no single coordinator
- Event-Driven Architecture: components publish/subscribe to events
- When to use each pattern

Key Concept: Orchestration = central control; Choreography = distributed control via events.

Reference: Chapter 7 - Composability and Connectors
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


# ============================================================================
# SCENARIO: Order Fulfillment (same domain, two styles)
# ============================================================================
# Orchestration: OrderOrchestrator calls Inventory, Payment, Shipping in sequence
# Choreography: OrderPlaced event → Inventory reserves → Payment charges → Shipping ships
#              Each subscriber reacts independently; no central driver


# ============================================================================
# ORCHESTRATION: Central coordinator
# ============================================================================

class OrderOrchestrator:
    """
    Orchestration: This component CONTROLS the flow.
    It calls each service in order and decides what to do next.
    """
    
    def __init__(
        self,
        inventory: Callable[[str, int], bool],
        payment: Callable[[str, float], bool],
        shipping: Callable[[str, str], str],
        notifier: Callable[[str, str], None],
    ) -> None:
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notifier = notifier
    
    def fulfill_order(self, order_id: str, item_id: str, qty: int, total: float, email: str, address: str) -> Dict:
        # Orchestrator decides the sequence
        if not self._inventory(item_id, qty):
            return {"status": "failed", "reason": "out_of_stock"}
        if not self._payment(order_id, total):
            return {"status": "failed", "reason": "payment_failed"}
        shipment_id = self._shipping(order_id, address)
        self._notifier(email, f"Shipped: {shipment_id}")
        return {"status": "ok", "shipment_id": shipment_id}


# ============================================================================
# CHOREOGRAPHY: Event bus, no central coordinator
# ============================================================================

@dataclass
class Event:
    """Domain event."""
    name: str
    payload: Dict


class EventBus:
    """Simple event bus: subscribers react to events."""
    
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[Event], None]]] = {}
    
    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_name, []).append(handler)
    
    def publish(self, event: Event) -> None:
        for h in self._handlers.get(event.name, []):
            h(event)


# Components in choreography: react to events, may publish new events

class InventoryChoreography:
    def __init__(self, bus: EventBus) -> None:
        self._stock = {"item-A": 10}
        bus.subscribe("OrderPlaced", self.handle_order_placed)
    
    def handle_order_placed(self, event: Event) -> None:
        order_id = event.payload["order_id"]
        item_id = event.payload["item_id"]
        qty = event.payload.get("qty", 1)
        if self._stock.get(item_id, 0) >= qty:
            self._stock[item_id] -= qty
            event.payload["_inventory_ok"] = True
        else:
            event.payload["_inventory_ok"] = False


class PaymentChoreography:
    def __init__(self, bus: EventBus) -> None:
        bus.subscribe("OrderPlaced", self.handle_order_placed)
    
    def handle_order_placed(self, event: Event) -> None:
        if not event.payload.get("_inventory_ok"):
            return
        order_id = event.payload["order_id"]
        total = event.payload["total"]
        # Simulate charge
        event.payload["_payment_ok"] = total > 0


class ShippingChoreography:
    def __init__(self, bus: EventBus) -> None:
        bus.subscribe("OrderPlaced", self.handle_order_placed)
    
    def handle_order_placed(self, event: Event) -> None:
        if not event.payload.get("_payment_ok"):
            return
        order_id = event.payload["order_id"]
        address = event.payload["address"]
        shipment_id = f"SHIP-{order_id}-001"
        event.payload["shipment_id"] = shipment_id


# ============================================================================
# COMPARISON
# ============================================================================

def demonstrate_orchestration() -> None:
    print("\n--- ORCHESTRATION ---")
    
    def reserve(item_id: str, qty: int) -> bool:
        return item_id == "item-A" and qty <= 10
    
    def charge(order_id: str, amount: float) -> bool:
        return amount > 0
    
    def ship(order_id: str, address: str) -> str:
        return f"SHIP-{order_id}"
    
    def notify(email: str, msg: str) -> None:
        print(f"    Notify {email}: {msg}")
    
    orch = OrderOrchestrator(reserve, charge, ship, notify)
    result = orch.fulfill_order("O1", "item-A", 2, 50.0, "a@b.com", "123 St")
    print("  Result:", result)


def demonstrate_choreography() -> None:
    print("\n--- CHOREOGRAPHY ---")
    
    bus = EventBus()
    InventoryChoreography(bus)
    PaymentChoreography(bus)
    ShippingChoreography(bus)
    
    # No orchestrator: just publish event; subscribers react
    event = Event("OrderPlaced", {
        "order_id": "O2",
        "item_id": "item-A",
        "qty": 2,
        "total": 50.0,
        "email": "a@b.com",
        "address": "123 St",
    })
    bus.publish(event)
    print("  Event payload after choreography:", event.payload)


def show_comparison() -> None:
    print("\n" + "="*70)
    print("ORCHESTRATION vs CHOREOGRAPHY")
    print("="*70)
    print("""
ORCHESTRATION:
  • One component (orchestrator) controls the flow
  • It calls services in a defined sequence
  • Pros: Simple to follow, easy to change flow in one place
  • Cons: Orchestrator can become bottleneck; tight coupling to flow

CHOREOGRAPHY:
  • No central coordinator; components react to events
  • Each component subscribes to events and may publish new ones
  • Pros: Loose coupling, scalable, components can be added/removed
  • Cons: Harder to see overall flow; eventual consistency

EVENT-DRIVEN:
  • Event bus / message broker connects components
  • Components: publish events, subscribe to events
  • Enables choreography and async processing

WHEN TO USE:
  • Orchestration: bounded workflow, need strict sequence, single tenant
  • Choreography: distributed system, many independent consumers, scalability
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Example 2: Orchestration vs Choreography")
    print("="*70)
    demonstrate_orchestration()
    demonstrate_choreography()
    show_comparison()
