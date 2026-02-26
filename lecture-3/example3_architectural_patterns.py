#!/usr/bin/env python3
"""
Example 3: Architectural Patterns vs. Design Patterns

This example demonstrates:
- Architectural Patterns: System-wide structural patterns
- Design Patterns: Component-level implementation patterns
- Common architectural patterns: Layered, MVC, Microservices, Event-Driven
- How patterns solve recurring problems
- When to use which pattern

Key Concept: Architectural patterns address system structure.
Design patterns address component implementation.
"""

from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


# ============================================================================
# BUSINESS SCENARIO: Content Management System
# ============================================================================
# Different architectural patterns can be applied to the same problem
# Each pattern has different trade-offs


# ============================================================================
# ARCHITECTURAL PATTERNS (System-Wide)
# ============================================================================

class ArchitecturalPattern(Enum):
    """Common architectural patterns"""
    LAYERED = "layered"
    MVC = "model_view_controller"
    MICROSERVICES = "microservices"
    EVENT_DRIVEN = "event_driven"
    PIPE_AND_FILTER = "pipe_and_filter"
    CLIENT_SERVER = "client_server"
    PEER_TO_PEER = "peer_to_peer"


@dataclass
class PatternDescription:
    """Description of an architectural pattern"""
    name: str
    description: str
    components: List[str]
    connectors: List[str]
    benefits: List[str]
    drawbacks: List[str]
    use_cases: List[str]
    
    def describe(self):
        print(f"\n{'='*70}")
        print(f"ARCHITECTURAL PATTERN: {self.name}")
        print(f"{'='*70}")
        print(f"\nDescription: {self.description}")
        print(f"\nComponents: {', '.join(self.components)}")
        print(f"Connectors: {', '.join(self.connectors)}")
        print(f"\nBenefits:")
        for benefit in self.benefits:
            print(f"  ✓ {benefit}")
        print(f"\nDrawbacks:")
        for drawback in self.drawbacks:
            print(f"  ✗ {drawback}")
        print(f"\nUse Cases:")
        for use_case in self.use_cases:
            print(f"  • {use_case}")


# ============================================================================
# DESIGN PATTERNS (Component-Level)
# ============================================================================

class DesignPattern(Enum):
    """Common design patterns"""
    REPOSITORY = "repository"
    FACTORY = "factory"
    STRATEGY = "strategy"
    OBSERVER = "observer"
    SINGLETON = "singleton"
    ADAPTER = "adapter"
    FACADE = "facade"


@dataclass
class DesignPatternDescription:
    """Description of a design pattern"""
    name: str
    description: str
    problem: str
    solution: str
    scope: str  # "class", "object", "component"
    
    def describe(self):
        print(f"\n{'─'*70}")
        print(f"DESIGN PATTERN: {self.name} (Scope: {self.scope})")
        print(f"{'─'*70}")
        print(f"Problem: {self.problem}")
        print(f"Solution: {self.solution}")
        print(f"Description: {self.description}")


# ============================================================================
# PATTERN CATALOG
# ============================================================================

class PatternCatalog:
    """Catalog of architectural and design patterns"""
    
    @staticmethod
    def get_architectural_patterns() -> Dict[ArchitecturalPattern, PatternDescription]:
        """Get descriptions of architectural patterns"""
        return {
            ArchitecturalPattern.LAYERED: PatternDescription(
                name="Layered Architecture",
                description="Organizes system into horizontal layers, each providing services to the layer above",
                components=["Presentation Layer", "Business Logic Layer", "Data Access Layer", "Database Layer"],
                connectors=["Direct calls", "Function calls", "Method invocations"],
                benefits=[
                    "Clear separation of concerns",
                    "Easy to understand and maintain",
                    "Layers can be developed independently",
                    "Good for traditional business applications"
                ],
                drawbacks=[
                    "Performance overhead from layer traversal",
                    "Changes can cascade through layers",
                    "Can lead to \"fat\" layers",
                    "Not ideal for high-performance systems"
                ],
                use_cases=[
                    "Traditional enterprise applications",
                    "Web applications with clear tiers",
                    "Systems with well-defined responsibilities"
                ]
            ),
            
            ArchitecturalPattern.MVC: PatternDescription(
                name="Model-View-Controller",
                description="Separates application into three interconnected components: Model (data), View (UI), Controller (logic)",
                components=["Model", "View", "Controller"],
                connectors=["Observer pattern", "Direct calls", "Event notifications"],
                benefits=[
                    "Separation of concerns",
                    "Multiple views of same data",
                    "Easy to test business logic",
                    "UI changes don't affect business logic"
                ],
                drawbacks=[
                    "Can become complex with many views",
                    "Tight coupling between view and controller possible",
                    "Requires discipline to maintain separation"
                ],
                use_cases=[
                    "Web applications",
                    "Desktop GUI applications",
                    "Mobile applications",
                    "Systems with multiple user interfaces"
                ]
            ),
            
            ArchitecturalPattern.MICROSERVICES: PatternDescription(
                name="Microservices",
                description="Decomposes application into small, independent services that communicate over well-defined APIs",
                components=["Multiple independent services", "API Gateway", "Service Registry", "Databases per service"],
                connectors=["REST APIs", "Message Queues", "Event Bus", "Service Discovery"],
                benefits=[
                    "Independent deployment and scaling",
                    "Technology diversity",
                    "Fault isolation",
                    "Team autonomy"
                ],
                drawbacks=[
                    "Increased complexity",
                    "Distributed system challenges",
                    "Data consistency issues",
                    "Network latency",
                    "Operational overhead"
                ],
                use_cases=[
                    "Large, complex applications",
                    "Systems requiring independent scaling",
                    "Organizations with multiple teams",
                    "Systems with diverse technology needs"
                ]
            ),
            
            ArchitecturalPattern.EVENT_DRIVEN: PatternDescription(
                name="Event-Driven Architecture",
                description="Components communicate through events, enabling loose coupling and asynchronous processing",
                components=["Event Producers", "Event Consumers", "Event Bus", "Event Store"],
                connectors=["Event Bus", "Message Queue", "Pub/Sub"],
                benefits=[
                    "Loose coupling between components",
                    "Asynchronous processing",
                    "Scalability",
                    "Real-time responsiveness"
                ],
                drawbacks=[
                    "Eventual consistency",
                    "Complex debugging",
                    "Event ordering challenges",
                    "Testing complexity"
                ],
                use_cases=[
                    "Real-time systems",
                    "Systems with many independent components",
                    "Event sourcing applications",
                    "IoT systems"
                ]
            )
        }
    
    @staticmethod
    def get_design_patterns() -> Dict[DesignPattern, DesignPatternDescription]:
        """Get descriptions of design patterns"""
        return {
            DesignPattern.REPOSITORY: DesignPatternDescription(
                name="Repository Pattern",
                description="Abstracts data access logic, providing a collection-like interface",
                problem="Business logic is tightly coupled to data access implementation",
                solution="Create an abstraction layer between business logic and data access",
                scope="component"
            ),
            
            DesignPattern.FACTORY: DesignPatternDescription(
                name="Factory Pattern",
                description="Creates objects without specifying the exact class of object to be created",
                problem="Need to create objects without knowing their exact types",
                solution="Use a factory method or class to create objects",
                scope="class"
            ),
            
            DesignPattern.STRATEGY: DesignPatternDescription(
                name="Strategy Pattern",
                description="Defines a family of algorithms, encapsulates each one, and makes them interchangeable",
                problem="Need to switch between different algorithms at runtime",
                solution="Define algorithms as separate classes and make them interchangeable",
                scope="object"
            ),
            
            DesignPattern.OBSERVER: DesignPatternDescription(
                name="Observer Pattern",
                description="Notifies multiple objects about state changes",
                problem="Objects need to be notified when another object changes state",
                solution="Define a one-to-many dependency between objects",
                scope="object"
            )
        }


# ============================================================================
# EXAMPLE: Applying Patterns
# ============================================================================

def demonstrate_architectural_patterns():
    """Show different architectural patterns"""
    
    print("\n" + "="*70)
    print("ARCHITECTURAL PATTERNS vs. DESIGN PATTERNS")
    print("="*70)
    
    catalog = PatternCatalog()
    arch_patterns = catalog.get_architectural_patterns()
    design_patterns = catalog.get_design_patterns()
    
    # Show architectural patterns
    print("\n" + "="*70)
    print("ARCHITECTURAL PATTERNS (System-Wide Structure)")
    print("="*70)
    
    for pattern, description in arch_patterns.items():
        description.describe()
    
    # Show design patterns
    print("\n" + "="*70)
    print("DESIGN PATTERNS (Component-Level Implementation)")
    print("="*70)
    
    for pattern, description in design_patterns.items():
        description.describe()
    
    # ========================================================================
    # EXAMPLE: Content Management System with Different Patterns
    # ========================================================================
    
    print("\n" + "="*70)
    print("EXAMPLE: Content Management System")
    print("="*70)
    
    print("""
SCENARIO: Build a Content Management System (CMS)

OPTION 1: Layered Architecture
  • Presentation Layer: Web UI, Admin Panel
  • Business Logic Layer: Content Management, User Management
  • Data Access Layer: Database operations
  • Database Layer: PostgreSQL
  • Design Patterns Used: Repository, Factory
  
OPTION 2: MVC Architecture
  • Model: Content, User, Category models
  • View: HTML templates, JSON APIs
  • Controller: ContentController, UserController
  • Design Patterns Used: Repository, Strategy, Observer
  
OPTION 3: Microservices Architecture
  • Content Service: Manages articles, pages
  • User Service: Manages users and authentication
  • Media Service: Handles file uploads
  • Search Service: Provides search functionality
  • Design Patterns Used: API Gateway, Service Discovery, Circuit Breaker
  
OPTION 4: Event-Driven Architecture
  • Content Service: Publishes content events
  • Search Service: Consumes content events to update index
  • Notification Service: Consumes events to send notifications
  • Analytics Service: Consumes events for analytics
  • Design Patterns Used: Event Sourcing, CQRS, Observer
    """)


# ============================================================================
# KEY DIFFERENCES
# ============================================================================

def show_key_differences():
    """Show key differences between architectural and design patterns"""
    
    print("\n" + "="*70)
    print("KEY DIFFERENCES: Architectural vs. Design Patterns")
    print("="*70)
    print("""
ARCHITECTURAL PATTERNS:
  • Scope: System-wide, structural organization
  • Level: High-level system structure
  • Examples: Microservices, Layered, MVC, Event-Driven
  • Impact: Affects entire system
  • Change Cost: Very expensive to change
  • Questions: "How is the system organized?" 
              "What are the major components?"
  
DESIGN PATTERNS:
  • Scope: Component-level, implementation details
  • Level: Low-level code organization
  • Examples: Repository, Factory, Strategy, Observer
  • Impact: Affects specific components
  • Change Cost: Relatively easier to change
  • Questions: "How is this component implemented?"
              "What pattern solves this problem?"

RELATIONSHIP:
  • Architectural patterns define the overall structure
  • Design patterns implement components within that structure
  • Multiple design patterns can be used within one architectural pattern
  • Example: Microservices (architectural) can use Repository, Factory (design)
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_architectural_patterns()
    show_key_differences()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Architectural patterns define system-wide structure
✓ Design patterns define component-level implementation
✓ Architectural patterns are harder to change
✓ Design patterns are easier to change
✓ Multiple design patterns can be used within one architectural pattern
✓ Choose patterns based on problem requirements and constraints
    """)

