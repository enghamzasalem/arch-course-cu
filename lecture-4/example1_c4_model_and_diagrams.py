#!/usr/bin/env python3
"""
Example 1: C4 Model and Architecture Diagrams

This example demonstrates:
- C4 Model: Context, Container, Component, Code levels
- Architecture diagrams at different abstraction levels
- When to use each diagram type
- How models support stakeholder communication

Key Concept: The C4 model provides a hierarchical way to document
software architecture at different levels of detail.

Reference: https://c4model.com/
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# BUSINESS SCENARIO: Online Food Delivery System
# ============================================================================
# Level 1 (Context): System and external users/systems
# Level 2 (Container): Applications within the system
# Level 3 (Component): Components within each container
# Level 4 (Code): Implementation details (optional)


# ============================================================================
# C4 MODEL: Hierarchical Abstraction Levels
# ============================================================================

class C4Level(Enum):
    """C4 Model abstraction levels"""
    CONTEXT = 1   # System context - users and external systems
    CONTAINER = 2 # Software containers (applications)
    COMPONENT = 3 # Components within containers
    CODE = 4      # Code-level (classes, interfaces) - optional


@dataclass
class C4Element:
    """Base element in C4 model"""
    name: str
    description: str
    technology: Optional[str] = None
    
    def describe(self) -> str:
        tech = f" ({self.technology})" if self.technology else ""
        return f"{self.name}{tech}: {self.description}"


# ============================================================================
# LEVEL 1: SYSTEM CONTEXT
# ============================================================================

@dataclass
class Person:
    """External person (user) - Level 1"""
    name: str
    description: str


@dataclass
class ExternalSystem:
    """External system - Level 1"""
    name: str
    description: str


@dataclass
class SystemContext:
    """Level 1: System Context Diagram
    
    Shows: The system and its relationships with users and external systems.
    Audience: Everyone (technical and non-technical).
    """
    system_name: str
    system_description: str
    users: List[Person] = field(default_factory=list)
    external_systems: List[ExternalSystem] = field(default_factory=list)
    relationships: List[tuple] = field(default_factory=list)
    
    def describe(self):
        print("\n" + "="*70)
        print("C4 LEVEL 1: SYSTEM CONTEXT DIAGRAM")
        print("="*70)
        print(f"\nSystem: {self.system_name}")
        print(f"Description: {self.system_description}")
        print(f"\nUsers (Persons):")
        for u in self.users:
            print(f"  • {u.name}: {u.description}")
        print(f"\nExternal Systems:")
        for ext in self.external_systems:
            print(f"  • {ext.name}: {ext.description}")
        print(f"\nRelationships:")
        for rel in self.relationships:
            print(f"  • {rel[0]} → {rel[1]}: {rel[2]}")
        print("\nDiagram elements: Person (stick figure), System (box), External (box)")


# ============================================================================
# LEVEL 2: CONTAINER DIAGRAM
# ============================================================================

@dataclass
class Container:
    """Software container (application/service) - Level 2"""
    name: str
    description: str
    technology: str
    responsibility: str
    
    def describe(self) -> str:
        return f"{self.name} [{self.technology}]: {self.description}"


@dataclass
class ContainerDiagram:
    """Level 2: Container Diagram
    
    Shows: High-level shape of the software architecture.
    Audience: Technical people inside and outside the software development team.
    """
    system_name: str
    containers: List[Container] = field(default_factory=list)
    relationships: List[tuple] = field(default_factory=list)
    
    def describe(self):
        print("\n" + "="*70)
        print("C4 LEVEL 2: CONTAINER DIAGRAM")
        print("="*70)
        print(f"\nSystem: {self.system_name}")
        print(f"\nContainers (Applications/Services):")
        for c in self.containers:
            print(f"  • {c.describe()}")
            print(f"    Responsibility: {c.responsibility}")
        print(f"\nRelationships:")
        for rel in self.relationships:
            print(f"  • {rel[0]} → {rel[1]}: {rel[2]}")
        print("\nDiagram elements: Containers (boxes with technology label)")


# ============================================================================
# LEVEL 3: COMPONENT DIAGRAM
# ============================================================================

@dataclass
class Component:
    """Component within a container - Level 3"""
    name: str
    description: str
    technology: Optional[str] = None
    
    def describe(self) -> str:
        tech = f" [{self.technology}]" if self.technology else ""
        return f"{self.name}{tech}: {self.description}"


@dataclass
class ComponentDiagram:
    """Level 3: Component Diagram
    
    Shows: How a container is made up of components.
    Audience: Developers.
    """
    container_name: str
    components: List[Component] = field(default_factory=list)
    relationships: List[tuple] = field(default_factory=list)
    
    def describe(self):
        print("\n" + "="*70)
        print(f"C4 LEVEL 3: COMPONENT DIAGRAM - {self.container_name}")
        print("="*70)
        print(f"\nComponents:")
        for c in self.components:
            print(f"  • {c.describe()}")
        print(f"\nRelationships:")
        for rel in self.relationships:
            print(f"  • {rel[0]} → {rel[1]}: {rel[2]}")
        print("\nDiagram elements: Components (boxes), Database (cylinder)")


# ============================================================================
# DIAGRAM TYPE CATALOG
# ============================================================================

@dataclass
class DiagramTypeInfo:
    """Information about a diagram type"""
    name: str
    c4_level: Optional[C4Level]
    purpose: str
    audience: List[str]
    elements: List[str]
    
    def describe(self):
        print(f"\n{'─'*60}")
        print(f"Diagram: {self.name}")
        print(f"{'─'*60}")
        print(f"Purpose: {self.purpose}")
        print(f"Audience: {', '.join(self.audience)}")
        print(f"Elements: {', '.join(self.elements)}")


# ============================================================================
# EXAMPLE: Online Food Delivery System
# ============================================================================

def demonstrate_c4_model():
    """Demonstrate C4 model for food delivery system"""
    
    print("\n" + "="*70)
    print("EXAMPLE: Online Food Delivery System - C4 Model")
    print("="*70)
    
    # --- Level 1: System Context ---
    context = SystemContext(
        system_name="Food delivery system",
        system_description="Allows customers to order food from restaurants and get it delivered",
        users=[
            Person("Customer", "Person who wants to order food"),
            Person("Restaurant staff", "Person who manages restaurant orders"),
            Person("Delivery driver", "Person who delivers orders"),
        ],
        external_systems=[
            ExternalSystem("Payment Gateway", "Processes payments"),
            ExternalSystem("Maps API", "Provides location and routing"),
            ExternalSystem("SMS Gateway", "Sends notifications"),
        ],
        relationships=[
            ("Customer", "Food delivery system", "Places orders, tracks delivery"),
            ("Restaurant staff", "Food delivery system", "Manages menu, accepts orders"),
            ("Delivery driver", "Food delivery system", "Views delivery tasks"),
            ("Food delivery system", "Payment Gateway", "Processes payments"),
            ("Food delivery system", "Maps API", "Gets routes and ETA"),
            ("Food delivery system", "SMS Gateway", "Sends order notifications"),
        ]
    )
    context.describe()
    
    # --- Level 2: Container Diagram ---
    containers = ContainerDiagram(
        system_name="Food delivery system",
        containers=[
            Container(
                "Web Application",
                "Customer-facing web app",
                "React SPA",
                "Browse restaurants, place orders, track delivery"
            ),
            Container(
                "Mobile App",
                "Customer and driver mobile apps",
                "React Native",
                "Order food, manage deliveries"
            ),
            Container(
                "API",
                "Backend API for all clients",
                "Node.js",
                "Business logic, orchestration"
            ),
            Container(
                "Order Service",
                "Handles order lifecycle",
                "Java/Spring",
                "Create, update, track orders"
            ),
            Container(
                "Database",
                "Persists order and user data",
                "PostgreSQL",
                "Data persistence"
            ),
        ],
        relationships=[
            ("Web Application", "API", "HTTPS/JSON"),
            ("Mobile App", "API", "HTTPS/JSON"),
            ("API", "Order Service", "gRPC"),
            ("Order Service", "Database", "SQL"),
        ]
    )
    containers.describe()
    
    # --- Level 3: Component Diagram (for API container) ---
    api_components = ComponentDiagram(
        container_name="API",
        components=[
            Component("OrderController", "Handles order HTTP endpoints", "Express"),
            Component("AuthController", "Handles authentication", "Express"),
            Component("OrderServiceClient", "Calls Order Service", "gRPC Client"),
            Component("UserRepository", "Accesses user data", "TypeORM"),
        ],
        relationships=[
            ("OrderController", "OrderServiceClient", "Creates/updates orders"),
            ("OrderController", "UserRepository", "Gets user info"),
            ("AuthController", "UserRepository", "Validates credentials"),
        ]
    )
    api_components.describe()


def show_diagram_types():
    """Show common architecture diagram types"""
    
    print("\n" + "="*70)
    print("ARCHITECTURE DIAGRAM TYPES (Chapter 4)")
    print("="*70)
    
    diagram_types = [
        DiagramTypeInfo(
            "System Context (C4 L1)",
            C4Level.CONTEXT,
            "Shows system boundary and external interactions",
            ["Everyone", "Stakeholders"],
            ["System", "Users", "External systems"]
        ),
        DiagramTypeInfo(
            "Container (C4 L2)",
            C4Level.CONTAINER,
            "Shows high-level software architecture",
            ["Developers", "DevOps", "Architects"],
            ["Containers", "Applications", "Databases"]
        ),
        DiagramTypeInfo(
            "Component (C4 L3)",
            C4Level.COMPONENT,
            "Shows internal structure of a container",
            ["Developers"],
            ["Components", "Interfaces"]
        ),
        DiagramTypeInfo(
            "Deployment",
            None,
            "Shows where software runs (infrastructure)",
            ["DevOps", "System admins"],
            ["Nodes", "Containers", "Network"]
        ),
        DiagramTypeInfo(
            "Sequence",
            None,
            "Shows interaction over time for a use case",
            ["Developers", "Testers"],
            ["Actors", "Components", "Messages"]
        ),
        DiagramTypeInfo(
            "Component & Connector",
            None,
            "Shows runtime structure and communication",
            ["Architects", "Developers"],
            ["Components", "Connectors"]
        ),
    ]
    
    for dt in diagram_types:
        dt.describe()
    
    print("\n" + "="*70)
    print("KEY CONCEPTS")
    print("="*70)
    print("""
C4 MODEL:
  • Context (L1): System + users + external systems
  • Container (L2): Applications within the system
  • Component (L3): Components within containers
  • Code (L4): Classes/interfaces (optional, often use UML)

WHY C4:
  • Hierarchical: Zoom in for more detail
  • Consistent notation across levels
  • Abstraction: Right detail for right audience
  • Tool-agnostic: Can use draw.io, Structurizr, etc.

DIAGRAM SELECTION:
  • Choose based on audience and purpose
  • Start with context, drill down as needed
  • Keep diagrams focused (one concern per diagram)
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_c4_model()
    show_diagram_types()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ C4 model provides 4 levels of architectural abstraction
✓ Context diagram: system boundary and external actors
✓ Container diagram: high-level applications/services
✓ Component diagram: internal structure of each container
✓ Choose diagram type based on audience and purpose
✓ Models support effective architecture communication
    """)
