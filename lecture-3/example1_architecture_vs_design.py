#!/usr/bin/env python3
"""
Example 1: Architecture vs. Design

This example demonstrates:
- Architecture: High-level structure, strategic decisions, system-wide concerns
- Design: Detailed implementation, tactical decisions, component-level concerns
- How architecture constrains design choices
- When to make architectural vs. design decisions

Key Concept: Architecture is about "what" and "why" at a high level.
Design is about "how" at a detailed level.
"""

from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


# ============================================================================
# BUSINESS SCENARIO: E-commerce Platform
# ============================================================================
# Architecture decisions: Microservices vs. Monolith, Database choice,
# Communication patterns, Deployment strategy
# Design decisions: Data structures, algorithms, class hierarchies,
# Method implementations, error handling


# ============================================================================
# ARCHITECTURAL LEVEL: High-level structure and strategic decisions
# ============================================================================

class ArchitectureStyle(Enum):
    """Architectural style - a strategic decision"""
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    LAYERED = "layered"
    EVENT_DRIVEN = "event_driven"


class CommunicationPattern(Enum):
    """How components communicate - an architectural decision"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    EVENT_BASED = "event_based"


@dataclass
class ArchitecturalDecision:
    """An architectural decision - strategic, system-wide, hard to change"""
    decision: str
    rationale: str
    alternatives: List[str]
    consequences: List[str]
    impact_scope: str  # "system-wide", "component", "cross-cutting"
    
    def __str__(self):
        return f"""
Architectural Decision: {self.decision}
Rationale: {self.rationale}
Alternatives Considered: {', '.join(self.alternatives)}
Consequences: {', '.join(self.consequences)}
Impact Scope: {self.impact_scope}
"""


class Architecture:
    """The architecture defines the high-level structure"""
    
    def __init__(self, style: ArchitectureStyle):
        self.style = style
        self.decisions: List[ArchitecturalDecision] = []
        self.components: List[str] = []
        self.connectors: List[str] = []
    
    def add_decision(self, decision: ArchitecturalDecision):
        """Add an architectural decision"""
        self.decisions.append(decision)
        print(f"✓ Architectural decision recorded: {decision.decision}")
    
    def define_component(self, component: str):
        """Define a system component"""
        self.components.append(component)
        print(f"✓ Component defined: {component}")
    
    def define_connector(self, connector: str):
        """Define how components connect"""
        self.connectors.append(connector)
        print(f"✓ Connector defined: {connector}")
    
    def describe(self):
        """Describe the architecture"""
        print("\n" + "="*70)
        print("ARCHITECTURE (High-Level Structure)")
        print("="*70)
        print(f"Style: {self.style.value}")
        print(f"\nComponents: {', '.join(self.components)}")
        print(f"Connectors: {', '.join(self.connectors)}")
        print(f"\nArchitectural Decisions ({len(self.decisions)}):")
        for decision in self.decisions:
            print(decision)


# ============================================================================
# DESIGN LEVEL: Detailed implementation and tactical decisions
# ============================================================================

class DesignPattern(Enum):
    """Design pattern - a tactical decision"""
    REPOSITORY = "repository"
    FACTORY = "factory"
    STRATEGY = "strategy"
    OBSERVER = "observer"
    SINGLETON = "singleton"


@dataclass
class DesignDecision:
    """A design decision - tactical, local, easier to change"""
    decision: str
    rationale: str
    pattern_used: Optional[DesignPattern]
    scope: str  # "class", "method", "component"
    
    def __str__(self):
        pattern = f" (Pattern: {self.pattern_used.value})" if self.pattern_used else ""
        return f"Design Decision: {self.decision}{pattern}\n  Rationale: {self.rationale}\n  Scope: {self.scope}"


class ComponentDesign:
    """The design implements the architecture"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.design_decisions: List[DesignDecision] = []
        self.data_structures: List[str] = []
        self.algorithms: List[str] = []
    
    def add_design_decision(self, decision: DesignDecision):
        """Add a design decision"""
        self.design_decisions.append(decision)
        print(f"  → Design decision: {decision.decision}")
    
    def use_data_structure(self, ds: str):
        """Choose a data structure"""
        self.data_structures.append(ds)
        print(f"  → Data structure: {ds}")
    
    def use_algorithm(self, algo: str):
        """Choose an algorithm"""
        self.algorithms.append(algo)
        print(f"  → Algorithm: {algo}")
    
    def describe(self):
        """Describe the design"""
        print(f"\n{'─'*70}")
        print(f"DESIGN: {self.component_name} (Detailed Implementation)")
        print(f"{'─'*70}")
        print(f"Data Structures: {', '.join(self.data_structures)}")
        print(f"Algorithms: {', '.join(self.algorithms)}")
        print(f"\nDesign Decisions ({len(self.design_decisions)}):")
        for decision in self.design_decisions:
            print(f"  {decision}")


# ============================================================================
# EXAMPLE: Architecture constrains design
# ============================================================================

def demonstrate_architecture_vs_design():
    """Show how architecture and design relate"""
    
    print("\n" + "="*70)
    print("EXAMPLE: E-commerce Platform")
    print("="*70)
    
    # ========================================================================
    # ARCHITECTURAL DECISIONS (Strategic, System-Wide)
    # ========================================================================
    
    architecture = Architecture(ArchitectureStyle.MICROSERVICES)
    
    # Architectural decision 1: Choose microservices
    arch_decision_1 = ArchitecturalDecision(
        decision="Use microservices architecture",
        rationale="Need independent scaling, deployment, and technology choices",
        alternatives=["Monolithic", "Layered", "Event-driven"],
        consequences=[
            "Better scalability per service",
            "Independent deployment",
            "Increased complexity in communication",
            "Need for service discovery"
        ],
        impact_scope="system-wide"
    )
    architecture.add_decision(arch_decision_1)
    
    # Architectural decision 2: Database per service
    arch_decision_2 = ArchitecturalDecision(
        decision="Each microservice has its own database",
        rationale="Service independence and data isolation",
        alternatives=["Shared database", "Database per service", "Saga pattern"],
        consequences=[
            "Data consistency challenges",
            "Need for distributed transactions or eventual consistency",
            "Better service isolation"
        ],
        impact_scope="system-wide"
    )
    architecture.add_decision(arch_decision_2)
    
    # Define components
    architecture.define_component("User Service")
    architecture.define_component("Product Service")
    architecture.define_component("Order Service")
    architecture.define_component("Payment Service")
    
    # Define connectors
    architecture.define_connector("REST API")
    architecture.define_connector("Message Queue (RabbitMQ)")
    
    architecture.describe()
    
    # ========================================================================
    # DESIGN DECISIONS (Tactical, Component-Level)
    # ========================================================================
    
    print("\n" + "="*70)
    print("DESIGN IMPLEMENTATIONS (Constrained by Architecture)")
    print("="*70)
    
    # Design for User Service
    user_service_design = ComponentDesign("User Service")
    
    design_decision_1 = DesignDecision(
        decision="Use Repository pattern for data access",
        rationale="Abstract database operations, enable testing with mocks",
        pattern_used=DesignPattern.REPOSITORY,
        scope="component"
    )
    user_service_design.add_design_decision(design_decision_1)
    
    design_decision_2 = DesignDecision(
        decision="Use HashMap for in-memory user cache",
        rationale="Fast O(1) lookups for frequently accessed users",
        pattern_used=None,
        scope="class"
    )
    user_service_design.add_design_decision(design_decision_2)
    
    user_service_design.use_data_structure("HashMap (for cache)")
    user_service_design.use_data_structure("PostgreSQL (for persistence)")
    user_service_design.use_algorithm("JWT token generation")
    user_service_design.use_algorithm("Password hashing (bcrypt)")
    
    user_service_design.describe()
    
    # Design for Order Service
    order_service_design = ComponentDesign("Order Service")
    
    design_decision_3 = DesignDecision(
        decision="Use Strategy pattern for payment processing",
        rationale="Support multiple payment methods (credit card, PayPal, etc.)",
        pattern_used=DesignPattern.STRATEGY,
        scope="component"
    )
    order_service_design.add_design_decision(design_decision_3)
    
    design_decision_4 = DesignDecision(
        decision="Use Priority Queue for order processing",
        rationale="Process premium orders before regular orders",
        pattern_used=None,
        scope="method"
    )
    order_service_design.add_design_decision(design_decision_4)
    
    order_service_design.use_data_structure("Priority Queue (for order queue)")
    order_service_design.use_data_structure("PostgreSQL (for order storage)")
    order_service_design.use_algorithm("Order validation")
    order_service_design.use_algorithm("Inventory check")
    
    order_service_design.describe()
    
    # ========================================================================
    # KEY DIFFERENCES
    # ========================================================================
    
    print("\n" + "="*70)
    print("KEY DIFFERENCES: Architecture vs. Design")
    print("="*70)
    print("""
ARCHITECTURE (Strategic):
  • Scope: System-wide, cross-cutting concerns
  • Timing: Early in project lifecycle
  • Change Cost: Very expensive to change
  • Examples: Microservices vs. Monolith, Database choice, 
              Communication patterns, Deployment strategy
  • Questions: "What components exist?" "How do they communicate?"
  
DESIGN (Tactical):
  • Scope: Component-level, local concerns
  • Timing: During implementation
  • Change Cost: Relatively easier to change
  • Examples: Data structures, Algorithms, Design patterns,
              Class hierarchies, Method implementations
  • Questions: "How is this component implemented?" 
              "What data structure should I use?"
  
RELATIONSHIP:
  • Architecture constrains design choices
  • Design implements the architecture
  • Good architecture enables good design
  • Bad architecture makes good design difficult
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_architecture_vs_design()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Architecture defines the high-level structure and strategic decisions
✓ Design implements the architecture with tactical decisions
✓ Architecture decisions are harder to change and have system-wide impact
✓ Design decisions are easier to change and have local impact
✓ Architecture constrains what design choices are possible
✓ Good architecture makes good design easier
    """)

