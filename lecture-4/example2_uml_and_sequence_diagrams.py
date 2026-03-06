#!/usr/bin/env python3
"""
Example 2: UML for Architecture and Sequence Diagrams

This example demonstrates:
- UML diagrams for architecture: Component, Deployment, Sequence
- Sequence diagrams: interactions over time
- When to use each UML diagram type
- Modeling notation and conventions

Key Concept: UML provides standard notation for modeling architecture.
Different diagram types serve different modeling purposes.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# BUSINESS SCENARIO: Library Management System
# ============================================================================
# UML Component Diagram: Software structure
# UML Deployment Diagram: Hardware/infrastructure
# UML Sequence Diagram: Order checkout flow


# ============================================================================
# UML COMPONENT DIAGRAM ELEMENTS
# ============================================================================

class UMLStereotype(Enum):
    """UML stereotypes for components"""
    COMPONENT = "<<component>>"
    INTERFACE = "<<interface>>"
    SERVICE = "<<service>>"
    LIBRARY = "<<library>>"


@dataclass
class UMLComponent:
    """UML Component - provides/requires interfaces"""
    name: str
    stereotype: UMLStereotype
    provided_interfaces: List[str] = field(default_factory=list)
    required_interfaces: List[str] = field(default_factory=list)
    
    def describe(self) -> str:
        provided = ", ".join(self.provided_interfaces) or "none"
        required = ", ".join(self.required_interfaces) or "none"
        return f"{self.name} {self.stereotype.value}\n  Provides: {provided}\n  Requires: {required}"


# ============================================================================
# UML DEPLOYMENT DIAGRAM ELEMENTS
# ============================================================================

@dataclass
class Node:
    """UML Node - execution environment (server, device)"""
    name: str
    node_type: str  # "device", "execution environment"
    artifacts: List[str] = field(default_factory=list)
    
    def describe(self) -> str:
        arts = ", ".join(self.artifacts) if self.artifacts else "none"
        return f"{self.name} [{self.node_type}]\n  Deploys: {arts}"


# ============================================================================
# UML SEQUENCE DIAGRAM ELEMENTS
# ============================================================================

@dataclass
class SequenceMessage:
    """Message in a sequence diagram"""
    from_actor: str
    to_actor: str
    message: str
    message_type: str  # "sync", "async", "return"
    
    def describe(self) -> str:
        arrow = "-->"
        if self.message_type == "return":
            arrow = "-->>"
        elif self.message_type == "async":
            arrow = "- ->>"
        return f"{self.from_actor} {arrow} {self.to_actor}: {self.message}"


@dataclass
class SequenceDiagram:
    """UML Sequence Diagram - interaction over time
    
    Shows: Messages exchanged between actors/objects in chronological order.
    Purpose: Document use cases, API flows, request handling.
    """
    name: str
    participants: List[str] = field(default_factory=list)
    messages: List[SequenceMessage] = field(default_factory=list)
    
    def describe(self):
        print("\n" + "="*70)
        print(f"SEQUENCE DIAGRAM: {self.name}")
        print("="*70)
        print(f"\nParticipants: {' | '.join(self.participants)}")
        print(f"\nMessage Flow:")
        for i, msg in enumerate(self.messages, 1):
            arrow = "→" if msg.message_type == "sync" else "⇒"
            if msg.message_type == "return":
                arrow = "←"
            print(f"  {i}. {msg.from_actor} {arrow} {msg.to_actor}: {msg.message}")
        print("\nDiagram: Lifelines (vertical), Messages (horizontal arrows)")


# ============================================================================
# EXAMPLE: Library System - Component Diagram
# ============================================================================

def demonstrate_component_diagram():
    """Show UML component diagram for library system"""
    
    print("\n" + "="*70)
    print("UML COMPONENT DIAGRAM: Library Management System")
    print("="*70)
    
    components = [
        UMLComponent(
            "WebUI",
            UMLStereotype.COMPONENT,
            provided_interfaces=["IUserInterface"],
            required_interfaces=["IBookService", "IUserService"]
        ),
        UMLComponent(
            "BookService",
            UMLStereotype.SERVICE,
            provided_interfaces=["IBookService"],
            required_interfaces=["IBookRepository"]
        ),
        UMLComponent(
            "UserService",
            UMLStereotype.SERVICE,
            provided_interfaces=["IUserService"],
            required_interfaces=["IUserRepository"]
        ),
        UMLComponent(
            "BookRepository",
            UMLStereotype.COMPONENT,
            provided_interfaces=["IBookRepository"],
            required_interfaces=[]
        ),
        UMLComponent(
            "UserRepository",
            UMLStereotype.COMPONENT,
            provided_interfaces=["IUserRepository"],
            required_interfaces=[]
        ),
    ]
    
    print("\nComponents and Interfaces:")
    for c in components:
        print(f"\n{c.describe()}")
    
    print("\n" + "─"*70)
    print("Notation: Components (boxes), Interfaces (circles/lollipops)")
    print("Dependencies: Dashed arrows from required to provided interface")


# ============================================================================
# EXAMPLE: Library System - Deployment Diagram
# ============================================================================

def demonstrate_deployment_diagram():
    """Show UML deployment diagram"""
    
    print("\n" + "="*70)
    print("UML DEPLOYMENT DIAGRAM: Library System Infrastructure")
    print("="*70)
    
    nodes = [
        Node("Web Server", "execution environment", ["library-webapp.war"]),
        Node("App Server", "execution environment", ["library-api.jar"]),
        Node("Database Server", "device", ["PostgreSQL 15"]),
        Node("Load Balancer", "device", ["nginx"]),
    ]
    
    print("\nNodes and Artifacts:")
    for n in nodes:
        print(f"\n{n.describe()}")
    
    print("\n" + "─"*70)
    print("Connections: Web Server ↔ Load Balancer, App Server ↔ Database")
    print("Notation: Nodes (3D boxes), Artifacts (rectangles)")


# ============================================================================
# EXAMPLE: Sequence Diagram - Borrow Book Flow
# ============================================================================

def demonstrate_sequence_diagram():
    """Show sequence diagram for borrow book use case"""
    
    diagram = SequenceDiagram(
        name="Borrow Book - Successful Flow",
        participants=["Member", "WebUI", "BookService", "UserService", "Database"],
        messages=[
            SequenceMessage("Member", "WebUI", "Search for book", "sync"),
            SequenceMessage("WebUI", "BookService", "searchBooks(query)", "sync"),
            SequenceMessage("BookService", "Database", "SELECT * FROM books", "sync"),
            SequenceMessage("Database", "BookService", "book list", "return"),
            SequenceMessage("BookService", "WebUI", "Book[]", "return"),
            SequenceMessage("WebUI", "Member", "Display results", "sync"),
            SequenceMessage("Member", "WebUI", "Click Borrow", "sync"),
            SequenceMessage("WebUI", "BookService", "borrowBook(bookId, userId)", "sync"),
            SequenceMessage("BookService", "UserService", "checkBorrowLimit(userId)", "sync"),
            SequenceMessage("UserService", "Database", "SELECT COUNT(*) FROM loans", "sync"),
            SequenceMessage("Database", "UserService", "count", "return"),
            SequenceMessage("UserService", "BookService", "OK", "return"),
            SequenceMessage("BookService", "Database", "INSERT INTO loans", "sync"),
            SequenceMessage("BookService", "WebUI", "Success", "return"),
            SequenceMessage("WebUI", "Member", "Confirmation message", "sync"),
        ]
    )
    
    diagram.describe()


# ============================================================================
# MODELING NOTATION REFERENCE
# ============================================================================

def show_modeling_notation():
    """Show common modeling notations"""
    
    print("\n" + "="*70)
    print("MODELING NOTATION REFERENCE")
    print("="*70)
    print("""
UML DIAGRAM TYPES FOR ARCHITECTURE:

1. Component Diagram
   • Components: Boxes with <<stereotype>>
   • Interfaces: Circles (provided) / half-circles (required)
   • Dependencies: Dashed arrows
   • Shows: Static structure, interfaces, dependencies

2. Deployment Diagram
   • Nodes: 3D boxes (devices/servers)
   • Artifacts: Rectangles (deployable units)
   • Connections: Solid lines (communication paths)
   • Shows: Physical deployment, infrastructure

3. Sequence Diagram
   • Lifelines: Vertical dashed lines
   • Messages: Horizontal arrows (→ sync, ⇒ async, ← return)
   • Activation: Thin rectangles on lifelines
   • Shows: Temporal order of interactions

4. Class Diagram (for detailed design)
   • Classes: Boxes with name, attributes, methods
   • Associations: Lines with multiplicity
   • Shows: Static structure at code level

BEST PRACTICES:
  • Use consistent notation across diagrams
  • Keep diagrams focused (one concern)
  • Add legends for complex diagrams
  • Version control diagram files
  • Keep diagrams in sync with code
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_component_diagram()
    demonstrate_deployment_diagram()
    demonstrate_sequence_diagram()
    show_modeling_notation()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ UML Component Diagram: Static structure, interfaces, dependencies
✓ UML Deployment Diagram: Physical nodes, artifacts, infrastructure
✓ UML Sequence Diagram: Interactions over time, message flow
✓ Choose diagram type based on what you need to communicate
✓ Standard notation enables team communication
✓ Models should be maintained alongside code
    """)
