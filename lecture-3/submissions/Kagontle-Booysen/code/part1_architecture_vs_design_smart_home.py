#!/usr/bin/env python3
"""
Example: Architecture vs. Design (Smart Home Management System)

This example demonstrates:
- Architecture: high-level structure + strategic decisions (system-wide, hard to change)
- Design: detailed implementation choices (component-level, easier to change)
- How architectural choices constrain design options
- Use of quality attribute terminology (P1/P2/P3 priorities from Task 2.1)

Quality Attribute Priorities (from Task 2.1):
- Security (P1)
- Availability (P1)
- Performance (P2)
- Scalability (P2)
- Modifiability (P3)
- Testability (supporting)

Key Concept:
Architecture answers "WHAT exists?" and "HOW components interact?" and "WHY (quality attributes)?"
Design answers "HOW is a component implemented?" with patterns, data structures, and algorithms.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# =============================================================================
# ARCHITECTURAL LEVEL (Strategic, System-wide)
# =============================================================================

class ArchitectureStyle(Enum):
    MONOLITH = "Monolith"
    MICROSERVICES = "Microservices"
    LAYERED = "Layered"
    CLIENT_SERVER = "Client-Server"


class IntegrationStyle(Enum):
    REST_SYNC = "REST (Synchronous)"
    EVENT_DRIVEN = "Event-Driven (Async Pub/Sub)"


class QualityPriority(Enum):
    P1 = "P1 (Highest)"
    P2 = "P2"
    P3 = "P3"
    SUPPORTING = "Supporting"


@dataclass
class QualityAttribute:
    name: str
    priority: QualityPriority
    meaning: str  # short definition


@dataclass
class ArchitecturalDecision:
    decision: str
    rationale: str
    quality_attribute_drivers: List[QualityAttribute]
    alternatives: List[str]
    consequences: List[str]
    scope: str = "system-wide"

    def __str__(self) -> str:
        qa = ", ".join([f"{q.name} {q.priority.value}" for q in self.quality_attribute_drivers])
        return (
            f"\nArchitectural Decision: {self.decision}\n"
            f"Rationale: {self.rationale}\n"
            f"Quality Attribute Drivers: {qa}\n"
            f"Alternatives Considered: {', '.join(self.alternatives)}\n"
            f"Consequences: {', '.join(self.consequences)}\n"
            f"Impact Scope: {self.scope}\n"
        )


class Architecture:
    """Defines the high-level structure: components + connectors + decisions."""

    def __init__(self, system_name: str, style: ArchitectureStyle, integration: IntegrationStyle):
        self.system_name = system_name
        self.style = style
        self.integration = integration
        self.components: List[str] = []
        self.connectors: List[str] = []
        self.decisions: List[ArchitecturalDecision] = []

    def define_component(self, name: str) -> None:
        self.components.append(name)
        print(f"✓ Component defined: {name}")

    def define_connector(self, name: str) -> None:
        self.connectors.append(name)
        print(f"✓ Connector defined: {name}")

    def add_decision(self, adr: ArchitecturalDecision) -> None:
        self.decisions.append(adr)
        print(f"✓ Architectural decision recorded: {adr.decision}")

    def describe(self) -> None:
        print("\n" + "=" * 80)
        print(f"ARCHITECTURE (High-Level) — {self.system_name}")
        print("=" * 80)
        print(f"Style: {self.style.value}")
        print(f"Integration: {self.integration.value}")
        print(f"\nComponents ({len(self.components)}): {', '.join(self.components)}")
        print(f"Connectors ({len(self.connectors)}): {', '.join(self.connectors)}")
        print(f"\nArchitectural Decisions ({len(self.decisions)}):")
        for d in self.decisions:
            print(d)


# =============================================================================
# DESIGN LEVEL (Tactical, Component-level)
# =============================================================================

class DesignPattern(Enum):
    REPOSITORY = "Repository"
    STRATEGY = "Strategy"
    OBSERVER = "Observer"
    FACTORY = "Factory"
    CIRCUIT_BREAKER = "Circuit Breaker"


@dataclass
class DesignDecision:
    decision: str
    rationale: str
    pattern_used: Optional[DesignPattern]
    scope: str  # class / method / component

    def __str__(self) -> str:
        p = f" (Pattern: {self.pattern_used.value})" if self.pattern_used else ""
        return f"Design Decision: {self.decision}{p}\n  Rationale: {self.rationale}\n  Scope: {self.scope}"


class ComponentDesign:
    """Implements one component within architectural constraints."""

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.design_decisions: List[DesignDecision] = []
        self.data_structures: List[str] = []
        self.algorithms: List[str] = []

    def add_design_decision(self, dd: DesignDecision) -> None:
        self.design_decisions.append(dd)
        print(f"  → Design decision: {dd.decision}")

    def use_data_structure(self, ds: str) -> None:
        self.data_structures.append(ds)
        print(f"  → Data structure: {ds}")

    def use_algorithm(self, algo: str) -> None:
        self.algorithms.append(algo)
        print(f"  → Algorithm: {algo}")

    def describe(self) -> None:
        print("\n" + "─" * 80)
        print(f"DESIGN (Detailed) — {self.component_name}")
        print("─" * 80)
        print(f"Data Structures: {', '.join(self.data_structures) if self.data_structures else 'N/A'}")
        print(f"Algorithms: {', '.join(self.algorithms) if self.algorithms else 'N/A'}")
        print(f"\nDesign Decisions ({len(self.design_decisions)}):")
        for d in self.design_decisions:
            print(f"  {d}")


# =============================================================================
# DEMO: Smart Home Architecture constrains Smart Home Design
# =============================================================================

def demonstrate_architecture_vs_design_smart_home() -> None:
    # Quality attributes (Task 2.1 terminology)
    security = QualityAttribute("Security", QualityPriority.P1, "Prevent unauthorized access to devices/data")
    availability = QualityAttribute("Availability", QualityPriority.P1, "System remains operational during failures")
    performance = QualityAttribute("Performance", QualityPriority.P2, "Low latency device control and alert delivery")
    scalability = QualityAttribute("Scalability", QualityPriority.P2, "Handle more devices/events/users without degradation")
    modifiability = QualityAttribute("Modifiability", QualityPriority.P3, "Ease of change and extension over time")

    print("\n" + "=" * 80)
    print("EXAMPLE: Smart Home Management System")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # ARCHITECTURE (Strategic)
    # -------------------------------------------------------------------------
    arch = Architecture(
        system_name="Smart Home Management System",
        style=ArchitectureStyle.MICROSERVICES,
        integration=IntegrationStyle.EVENT_DRIVEN,
    )

    # Define components (what exists)
    for c in [
        "Mobile App",
        "Web App",
        "Voice Assistant Integration",
        "API Gateway",
        "Identity Service",
        "Device Manager Service",
        "Automation Service",
        "Notification Service",
        "Event Bus / Broker",
        "Datastores (per-service)",
        "IoT Hub / Devices",
    ]:
        arch.define_component(c)

    # Define connectors (how they communicate)
    for k in [
        "HTTPS/REST (Clients -> API Gateway)",
        "mTLS/REST (Gateway -> Services)",
        "Async Pub/Sub (Services <-> Event Bus)",
        "MQTT/WebSocket (Device Manager <-> IoT Hub/Devices)",
        "SQL/NoSQL Connections (Service -> Own DB)",
    ]:
        arch.define_connector(k)

    # Architectural Decision 1: Microservices
    arch.add_decision(ArchitecturalDecision(
        decision="Adopt Microservices Architecture (domain-oriented services)",
        rationale=(
            "Support independent scaling and deployment of Device Control, Automation, and Notifications, "
            "and reduce coupling across business domains."
        ),
        quality_attribute_drivers=[availability, scalability, modifiability],
        alternatives=["Monolith", "Layered monolith", "Client-Server (single backend)"],
        consequences=[
            "Improves fault isolation and independent scaling (QA: Availability P1, Scalability P2)",
            "Increases operational complexity (monitoring, tracing, deployment)",
            "Introduces distributed system challenges (latency, eventual consistency)"
        ],
        scope="system-wide"
    ))

    # Architectural Decision 2: Event-driven integration
    arch.add_decision(ArchitecturalDecision(
        decision="Use Event-Driven Pub/Sub for device events, alerts, and automation triggers",
        rationale=(
            "Smart home behavior is asynchronous and bursty; pub/sub decouples producers and consumers "
            "and supports fan-out to Automation and Notification services."
        ),
        quality_attribute_drivers=[availability, scalability, performance, modifiability],
        alternatives=["Pure synchronous REST", "Direct database sharing", "Point-to-point message queues only"],
        consequences=[
            "Improves resilience via buffering and async processing (QA: Availability P1)",
            "Improves extensibility (new subscribers without changing producers) (QA: Modifiability P3)",
            "Requires schema/version governance and idempotent consumers"
        ],
        scope="system-wide"
    ))

    # Architectural Decision 3: API Gateway
    arch.add_decision(ArchitecturalDecision(
        decision="Use an API Gateway as the single entry point for all clients",
        rationale=(
            "Centralize cross-cutting concerns (authentication verification, rate limiting, request validation, observability) "
            "to strengthen security and simplify client integration."
        ),
        quality_attribute_drivers=[security, availability, performance],
        alternatives=["Clients call services directly", "Separate BFF per client channel"],
        consequences=[
            "Consistent policy enforcement (QA: Security P1)",
            "Potential bottleneck if gateway becomes overloaded (mitigate by keeping it thin)",
            "Improved monitoring and traffic management"
        ],
        scope="cross-cutting"
    ))

    arch.describe()

    # -------------------------------------------------------------------------
    # DESIGN (Tactical) — Implementing components within the architecture
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("DESIGN IMPLEMENTATIONS (Constrained by Architecture)")
    print("=" * 80)

    # DESIGN: Device Manager Service (component-level choices)
    device_design = ComponentDesign("Device Manager Service")

    device_design.add_design_decision(DesignDecision(
        decision="Use Cache-Aside strategy for device state cache (in-memory)",
        rationale="Reduce read latency for frequent device state requests while keeping DB as source of truth.",
        pattern_used=DesignPattern.REPOSITORY,  # using repository layer around storage/cache
        scope="component"
    ))
    device_design.use_data_structure("LRU Cache (device state)")
    device_design.use_data_structure("Device Registry Map (hash map keyed by DeviceId)")
    device_design.use_algorithm("Idempotent command handler (dedupe by commandId)")
    device_design.use_algorithm("Optimistic concurrency control for state updates")

    device_design.describe()

    # DESIGN: Notification Service
    notif_design = ComponentDesign("Notification Service")

    notif_design.add_design_decision(DesignDecision(
        decision="Use Observer pattern for multi-channel notification fan-out",
        rationale="One alert event should notify multiple channels (push/email/SMS) without hard coupling.",
        pattern_used=DesignPattern.OBSERVER,
        scope="component"
    ))
    notif_design.add_design_decision(DesignDecision(
        decision="Use Circuit Breaker for external SMS/Email provider calls",
        rationale="Prevent cascading failures and improve availability when third-party providers degrade.",
        pattern_used=DesignPattern.CIRCUIT_BREAKER,
        scope="method"
    ))
    notif_design.use_data_structure("Retry Queue (in-memory or broker-backed)")
    notif_design.use_algorithm("Exponential backoff + jitter retries")
    notif_design.use_algorithm("Template rendering for alert messages")

    notif_design.describe()

    # DESIGN: Automation Service
    auto_design = ComponentDesign("Automation Service")

    auto_design.add_design_decision(DesignDecision(
        decision="Use Strategy pattern for rule evaluation (trigger/condition/action)",
        rationale="Support new automation rule types without modifying core engine logic.",
        pattern_used=DesignPattern.STRATEGY,
        scope="component"
    ))
    auto_design.use_data_structure("Rule index (by deviceId and trigger type)")
    auto_design.use_algorithm("Rule evaluation pipeline (trigger -> conditions -> actions)")
    auto_design.use_algorithm("Debounce logic for noisy sensors")

    auto_design.describe()

    # -------------------------------------------------------------------------
    # KEY DIFFERENCES (summary)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("KEY DIFFERENCES: Architecture vs. Design (Smart Home)")
    print("=" * 80)
    print(
        """
ARCHITECTURE (Strategic):
  • Scope: System-wide + cross-cutting concerns
  • Focus: Quality attribute drivers (Security P1, Availability P1, Performance/Scalability P2, Modifiability P3)
  • Change cost: High (impacts many components)
  • Examples:
      - Microservices vs Monolith
      - Event-driven pub/sub vs synchronous REST
      - API Gateway placement and responsibilities
  • Questions:
      - What are the major components?
      - How do they communicate?
      - Why (which quality attributes are being optimized)?

DESIGN (Tactical):
  • Scope: Component/class/method-level
  • Focus: Patterns, algorithms, data structures, error-handling strategies
  • Change cost: Lower (mostly local)
  • Examples:
      - Cache-aside device state caching strategy
      - Circuit breaker for provider resilience
      - Strategy pattern for automation rules
  • Questions:
      - How does a service implement its responsibilities?
      - What data structures and patterns achieve the requirements?

RELATIONSHIP:
  • Architecture constrains design (e.g., event-driven requires idempotency and schema management)
  • Design realizes architectural intent using concrete implementation choices
"""
    )


def main() -> None:
    demonstrate_architecture_vs_design_smart_home()


if __name__ == "__main__":
    main()
