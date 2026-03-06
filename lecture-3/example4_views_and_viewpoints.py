#!/usr/bin/env python3
"""
Example 4: Views and Viewpoints

This example demonstrates:
- Views: Representations of a system from a specific perspective
- Viewpoints: Templates or patterns for creating views
- Different stakeholders need different views
- Common viewpoints: Logical, Process, Development, Physical, Scenarios
- How views help communicate architecture

Key Concept: Different stakeholders need different views of the same system.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# BUSINESS SCENARIO: E-commerce Platform
# ============================================================================
# Different stakeholders need different views:
# - Developers: Component structure, code organization
# - DevOps: Deployment, infrastructure
# - Business: Capabilities, value streams
# - Security: Security boundaries, threats


# ============================================================================
# VIEWPOINTS: Templates for creating views
# ============================================================================

class Viewpoint(Enum):
    """Standard architectural viewpoints"""
    LOGICAL = "logical"
    PROCESS = "process"
    DEVELOPMENT = "development"
    PHYSICAL = "physical"
    SCENARIOS = "scenarios"
    DATA = "data"
    SECURITY = "security"


@dataclass
class ViewpointDescription:
    """Description of a viewpoint"""
    name: str
    description: str
    stakeholders: List[str]
    concerns: List[str]
    elements: List[str]
    relationships: List[str]
    
    def describe(self):
        print(f"\n{'='*70}")
        print(f"VIEWPOINT: {self.name}")
        print(f"{'='*70}")
        print(f"Description: {self.description}")
        print(f"\nStakeholders: {', '.join(self.stakeholders)}")
        print(f"\nConcerns:")
        for concern in self.concerns:
            print(f"  • {concern}")
        print(f"\nElements: {', '.join(self.elements)}")
        print(f"Relationships: {', '.join(self.relationships)}")


# ============================================================================
# VIEW: A specific representation from a viewpoint
# ============================================================================

@dataclass
class ArchitecturalView:
    """An architectural view of the system"""
    name: str
    viewpoint: Viewpoint
    description: str
    elements: Dict[str, str]  # element_name -> description
    relationships: List[tuple]  # (from, to, relationship_type)
    diagram_description: str
    
    def describe(self):
        print(f"\n{'='*70}")
        print(f"VIEW: {self.name}")
        print(f"{'='*70}")
        print(f"Viewpoint: {self.viewpoint.value}")
        print(f"Description: {self.description}")
        print(f"\nElements:")
        for element, desc in self.elements.items():
            print(f"  • {element}: {desc}")
        print(f"\nRelationships:")
        for from_elem, to_elem, rel_type in self.relationships:
            print(f"  • {from_elem} --[{rel_type}]--> {to_elem}")
        print(f"\nDiagram Description:")
        print(f"  {self.diagram_description}")


# ============================================================================
# VIEWPOINT CATALOG
# ============================================================================

class ViewpointCatalog:
    """Catalog of standard viewpoints"""
    
    @staticmethod
    def get_viewpoints() -> Dict[Viewpoint, ViewpointDescription]:
        """Get descriptions of standard viewpoints"""
        return {
            Viewpoint.LOGICAL: ViewpointDescription(
                name="Logical Viewpoint",
                description="Shows the functional decomposition of the system into logical components",
                stakeholders=["Architects", "Developers", "Business Analysts"],
                concerns=[
                    "What are the main functional components?",
                    "How is functionality organized?",
                    "What are the key abstractions?"
                ],
                elements=["Components", "Interfaces", "Services"],
                relationships=["Uses", "Depends on", "Provides"]
            ),
            
            Viewpoint.PROCESS: ViewpointDescription(
                name="Process Viewpoint",
                description="Shows the runtime behavior, processes, and threads",
                stakeholders=["Developers", "Performance Engineers", "System Administrators"],
                concerns=[
                    "What processes exist at runtime?",
                    "How do processes communicate?",
                    "What are the concurrency and synchronization concerns?"
                ],
                elements=["Processes", "Threads", "Tasks"],
                relationships=["Communicates with", "Synchronizes with", "Spawns"]
            ),
            
            Viewpoint.DEVELOPMENT: ViewpointDescription(
                name="Development Viewpoint",
                description="Shows the static organization of software in development environment",
                stakeholders=["Developers", "Project Managers"],
                concerns=[
                    "How is code organized?",
                    "What are the module dependencies?",
                    "How do teams work on different parts?"
                ],
                elements=["Modules", "Packages", "Libraries"],
                relationships=["Depends on", "Imports", "Contains"]
            ),
            
            Viewpoint.PHYSICAL: ViewpointDescription(
                name="Physical Viewpoint",
                description="Shows the deployment architecture and hardware infrastructure",
                stakeholders=["DevOps", "System Administrators", "Infrastructure Engineers"],
                concerns=[
                    "Where is software deployed?",
                    "What hardware is used?",
                    "How is the system distributed?"
                ],
                elements=["Nodes", "Devices", "Network"],
                relationships=["Deployed on", "Connected to", "Communicates via"]
            ),
            
            Viewpoint.SCENARIOS: ViewpointDescription(
                name="Scenarios Viewpoint",
                description="Shows how the system responds to specific use cases",
                stakeholders=["All stakeholders", "Testers", "Product Managers"],
                concerns=[
                    "How does the system handle specific use cases?",
                    "What is the flow of interactions?",
                    "How do components collaborate?"
                ],
                elements=["Actors", "Components", "Interactions"],
                relationships=["Interacts with", "Calls", "Responds to"]
            )
        }


# ============================================================================
# EXAMPLE: E-commerce Platform Views
# ============================================================================

def demonstrate_views_and_viewpoints():
    """Show different views of the same system"""
    
    print("\n" + "="*70)
    print("EXAMPLE: E-commerce Platform - Multiple Views")
    print("="*70)
    
    catalog = ViewpointCatalog()
    viewpoints = catalog.get_viewpoints()
    
    # Show viewpoints
    print("\n" + "="*70)
    print("STANDARD VIEWPOINTS")
    print("="*70)
    
    for viewpoint, description in viewpoints.items():
        description.describe()
    
    # ========================================================================
    # CREATE VIEWS FOR E-COMMERCE PLATFORM
    # ========================================================================
    
    print("\n" + "="*70)
    print("E-COMMERCE PLATFORM: DIFFERENT VIEWS")
    print("="*70)
    
    # Logical View
    logical_view = ArchitecturalView(
        name="E-commerce Platform - Logical View",
        viewpoint=Viewpoint.LOGICAL,
        description="Shows the functional components of the e-commerce system",
        elements={
            "User Management": "Handles user accounts, authentication, profiles",
            "Product Catalog": "Manages products, categories, inventory",
            "Shopping Cart": "Manages shopping cart operations",
            "Order Processing": "Handles order creation, payment, fulfillment",
            "Payment Gateway": "Processes payments with external providers",
            "Notification Service": "Sends emails, SMS, push notifications"
        },
        relationships=[
            ("User Management", "Shopping Cart", "provides user context"),
            ("Shopping Cart", "Order Processing", "creates orders"),
            ("Order Processing", "Payment Gateway", "processes payment"),
            ("Order Processing", "Notification Service", "sends notifications"),
            ("Product Catalog", "Shopping Cart", "provides product info")
        ],
        diagram_description="Boxes represent functional components. Arrows show dependencies and data flow."
    )
    logical_view.describe()
    
    # Physical View
    physical_view = ArchitecturalView(
        name="E-commerce Platform - Physical View",
        viewpoint=Viewpoint.PHYSICAL,
        description="Shows the deployment architecture and infrastructure",
        elements={
            "Web Server Cluster": "3 load-balanced web servers (AWS EC2)",
            "Application Server Cluster": "5 application servers (AWS EC2)",
            "Database Primary": "PostgreSQL primary (AWS RDS)",
            "Database Replica": "PostgreSQL read replica (AWS RDS)",
            "Redis Cache": "Redis cluster for caching (AWS ElastiCache)",
            "CDN": "CloudFront CDN for static assets",
            "Message Queue": "RabbitMQ cluster (AWS EC2)"
        },
        relationships=[
            ("Web Server Cluster", "Application Server Cluster", "load balanced"),
            ("Application Server Cluster", "Database Primary", "writes to"),
            ("Application Server Cluster", "Database Replica", "reads from"),
            ("Application Server Cluster", "Redis Cache", "caches in"),
            ("CDN", "Web Server Cluster", "serves static assets"),
            ("Application Server Cluster", "Message Queue", "publishes to")
        ],
        diagram_description="Boxes represent physical nodes. Arrows show network connections and data flow."
    )
    physical_view.describe()
    
    # Process View
    process_view = ArchitecturalView(
        name="E-commerce Platform - Process View",
        viewpoint=Viewpoint.PROCESS,
        description="Shows runtime processes and their interactions",
        elements={
            "Web Request Handler": "Handles HTTP requests (multi-threaded)",
            "Order Processing Worker": "Background worker for order processing",
            "Payment Processor": "Processes payments asynchronously",
            "Notification Sender": "Sends notifications in background",
            "Cache Updater": "Updates cache asynchronously"
        },
        relationships=[
            ("Web Request Handler", "Order Processing Worker", "queues order"),
            ("Order Processing Worker", "Payment Processor", "triggers payment"),
            ("Order Processing Worker", "Notification Sender", "sends notification"),
            ("Order Processing Worker", "Cache Updater", "updates cache")
        ],
        diagram_description="Boxes represent processes/threads. Arrows show asynchronous communication."
    )
    process_view.describe()
    
    # Scenarios View
    scenarios_view = ArchitecturalView(
        name="E-commerce Platform - Scenarios View: Place Order",
        viewpoint=Viewpoint.SCENARIOS,
        description="Shows the flow of placing an order",
        elements={
            "Customer": "User placing order",
            "Web Frontend": "User interface",
            "Shopping Cart Service": "Manages cart",
            "Order Service": "Creates order",
            "Payment Service": "Processes payment",
            "Inventory Service": "Reserves inventory",
            "Notification Service": "Sends confirmation"
        },
        relationships=[
            ("Customer", "Web Frontend", "clicks checkout"),
            ("Web Frontend", "Shopping Cart Service", "gets cart items"),
            ("Web Frontend", "Order Service", "creates order"),
            ("Order Service", "Payment Service", "processes payment"),
            ("Order Service", "Inventory Service", "reserves items"),
            ("Order Service", "Notification Service", "sends confirmation"),
            ("Notification Service", "Customer", "sends email")
        ],
        diagram_description="Sequence of interactions showing how components collaborate to fulfill a use case."
    )
    scenarios_view.describe()
    
    # ========================================================================
    # KEY CONCEPTS
    # ========================================================================
    
    print("\n" + "="*70)
    print("KEY CONCEPTS: Views and Viewpoints")
    print("="*70)
    print("""
VIEWPOINTS:
  • Templates or patterns for creating views
  • Define what elements and relationships to include
  • Standardized way to document architecture
  • Examples: Logical, Physical, Process, Development, Scenarios
  
VIEWS:
  • Specific representations of a system from a viewpoint
  • Created for specific stakeholders
  • Show relevant concerns and hide irrelevant details
  • Multiple views of the same system are complementary
  
STAKEHOLDERS NEED DIFFERENT VIEWS:
  • Developers: Logical, Development views
  • DevOps: Physical, Process views
  • Business: Logical, Scenarios views
  • Security: Security view, Logical view
  
BENEFITS:
  • Communication: Each stakeholder sees what they need
  • Documentation: Comprehensive architecture documentation
  • Analysis: Different views reveal different aspects
  • Maintenance: Views help understand system structure
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_views_and_viewpoints()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Viewpoints are templates for creating views
✓ Views are specific representations from viewpoints
✓ Different stakeholders need different views
✓ Multiple views are complementary, not contradictory
✓ Views help communicate architecture effectively
✓ Standard viewpoints provide common vocabulary
    """)

