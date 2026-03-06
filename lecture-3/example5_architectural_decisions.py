#!/usr/bin/env python3
"""
Example 5: Architectural Decisions and Technical Debt

This example demonstrates:
- Architectural Decision Records (ADRs)
- How to document architectural decisions
- Technical debt: What it is and how it accumulates
- Architectural smells: Warning signs of problems
- How to manage and pay down technical debt

Key Concept: Architectural decisions should be documented.
Technical debt accumulates when shortcuts are taken.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# BUSINESS SCENARIO: Growing Startup System
# ============================================================================
# As the system grows, architectural decisions accumulate
# Some decisions create technical debt
# Architectural smells indicate problems


# ============================================================================
# ARCHITECTURAL DECISION RECORD (ADR)
# ============================================================================

class DecisionStatus(Enum):
    """Status of an architectural decision"""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


@dataclass
class ArchitecturalDecisionRecord:
    """An Architectural Decision Record (ADR)"""
    id: int
    title: str
    status: DecisionStatus
    date: datetime
    context: str
    decision: str
    consequences: List[str]
    alternatives: List[str]
    related_decisions: List[int] = field(default_factory=list)
    
    def describe(self):
        print(f"\n{'='*70}")
        print(f"ADR #{self.id}: {self.title}")
        print(f"{'='*70}")
        print(f"Status: {self.status.value.upper()}")
        print(f"Date: {self.date.strftime('%Y-%m-%d')}")
        print(f"\nContext:")
        print(f"  {self.context}")
        print(f"\nDecision:")
        print(f"  {self.decision}")
        print(f"\nConsequences:")
        for consequence in self.consequences:
            print(f"  • {consequence}")
        print(f"\nAlternatives Considered:")
        for alternative in self.alternatives:
            print(f"  • {alternative}")
        if self.related_decisions:
            print(f"\nRelated ADRs: {', '.join(f'#{id}' for id in self.related_decisions)}")


# ============================================================================
# TECHNICAL DEBT
# ============================================================================

class TechnicalDebtType(Enum):
    """Types of technical debt"""
    ARCHITECTURAL = "architectural"
    CODE = "code"
    TEST = "test"
    DOCUMENTATION = "documentation"
    DEPENDENCY = "dependency"


@dataclass
class TechnicalDebtItem:
    """An item of technical debt"""
    id: str
    description: str
    debt_type: TechnicalDebtType
    severity: str  # "low", "medium", "high", "critical"
    interest: str  # How much it costs over time
    principal: str  # Cost to fix
    created_date: datetime
    impact: str
    
    def describe(self):
        print(f"\n{'─'*70}")
        print(f"Technical Debt: {self.id}")
        print(f"{'─'*70}")
        print(f"Type: {self.debt_type.value}")
        print(f"Severity: {self.severity.upper()}")
        print(f"Description: {self.description}")
        print(f"Impact: {self.impact}")
        print(f"Principal (fix cost): {self.principal}")
        print(f"Interest (ongoing cost): {self.interest}")
        print(f"Created: {self.created_date.strftime('%Y-%m-%d')}")


# ============================================================================
# ARCHITECTURAL SMELLS
# ============================================================================

class ArchitecturalSmell(Enum):
    """Common architectural smells"""
    GOD_COMPONENT = "god_component"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    SCATTERED_CONCERN = "scattered_concern"
    TANGLED_DEPENDENCIES = "tangled_dependencies"
    UNSTABLE_DEPENDENCIES = "unstable_dependencies"
    FEATURE_ENVY = "feature_envy"
    DATA_CLASS = "data_class"


@dataclass
class SmellDescription:
    """Description of an architectural smell"""
    name: str
    description: str
    symptoms: List[str]
    causes: List[str]
    solutions: List[str]
    
    def describe(self):
        print(f"\n{'─'*70}")
        print(f"ARCHITECTURAL SMELL: {self.name}")
        print(f"{'─'*70}")
        print(f"Description: {self.description}")
        print(f"\nSymptoms:")
        for symptom in self.symptoms:
            print(f"  • {symptom}")
        print(f"\nCommon Causes:")
        for cause in self.causes:
            print(f"  • {cause}")
        print(f"\nPossible Solutions:")
        for solution in self.solutions:
            print(f"  • {solution}")


# ============================================================================
# EXAMPLE: Startup System Evolution
# ============================================================================

def demonstrate_architectural_decisions():
    """Show architectural decisions over time"""
    
    print("\n" + "="*70)
    print("EXAMPLE: Startup System - Architectural Decisions Over Time")
    print("="*70)
    
    # Decision 1: Start with monolith
    adr1 = ArchitecturalDecisionRecord(
        id=1,
        title="Start with monolithic architecture",
        status=DecisionStatus.ACCEPTED,
        date=datetime(2020, 1, 15),
        context="We're a startup with 2 developers. Need to move fast and validate product-market fit.",
        decision="Build a monolithic application using Django. Deploy as single application.",
        consequences=[
            "Fast initial development",
            "Simple deployment",
            "Easy to understand for small team",
            "Will need to refactor later if we scale"
        ],
        alternatives=[
            "Microservices (too complex for small team)",
            "Serverless (vendor lock-in concerns)"
        ]
    )
    adr1.describe()
    
    # Decision 2: Add caching layer
    adr2 = ArchitecturalDecisionRecord(
        id=2,
        title="Add Redis caching layer",
        status=DecisionStatus.ACCEPTED,
        date=datetime(2020, 6, 20),
        context="Database queries are slow. User growth is increasing load.",
        decision="Add Redis cache for frequently accessed data. Cache user sessions, product listings, and search results.",
        consequences=[
            "Improved performance",
            "Reduced database load",
            "Additional infrastructure to manage",
            "Cache invalidation complexity"
        ],
        alternatives=[
            "Database query optimization (limited improvement)",
            "Add read replicas (more expensive)"
        ],
        related_decisions=[1]
    )
    adr2.describe()
    
    # Decision 3: Migrate to microservices (supersedes ADR 1)
    adr3 = ArchitecturalDecisionRecord(
        id=3,
        title="Migrate to microservices architecture",
        status=DecisionStatus.ACCEPTED,
        date=datetime(2021, 3, 10),
        context="Team has grown to 15 developers. Monolith is becoming a bottleneck. Need independent deployment.",
        decision="Break monolith into microservices: User Service, Product Service, Order Service, Payment Service.",
        consequences=[
            "Independent deployment and scaling",
            "Team autonomy",
            "Increased complexity",
            "Distributed system challenges",
            "Supersedes ADR #1"
        ],
        alternatives=[
            "Modular monolith (still single deployment)",
            "Service-oriented monolith (compromise)"
        ],
        related_decisions=[1, 2]
    )
    adr3.describe()


def demonstrate_technical_debt():
    """Show technical debt accumulation"""
    
    print("\n" + "="*70)
    print("TECHNICAL DEBT IN THE SYSTEM")
    print("="*70)
    
    # Technical debt items
    debt1 = TechnicalDebtItem(
        id="TD-001",
        description="No automated tests for critical payment flow",
        debt_type=TechnicalDebtType.TEST,
        severity="high",
        interest="Risk of bugs in production, manual testing takes 2 hours per release",
        principal="Write test suite: 3 days of work",
        created_date=datetime(2020, 2, 1),
        impact="High risk of payment bugs, slows down releases"
    )
    debt1.describe()
    
    debt2 = TechnicalDebtItem(
        id="TD-002",
        description="Shared database between services (violates microservices principle)",
        debt_type=TechnicalDebtType.ARCHITECTURAL,
        severity="critical",
        interest="Services are tightly coupled, can't scale independently, deployment coordination needed",
        principal="Split databases: 2 weeks of work + data migration",
        created_date=datetime(2021, 3, 15),
        impact="Prevents true service independence, limits scalability"
    )
    debt2.describe()
    
    debt3 = TechnicalDebtItem(
        id="TD-003",
        description="Outdated dependencies with known security vulnerabilities",
        debt_type=TechnicalDebtType.DEPENDENCY,
        severity="high",
        interest="Security risk, potential breaches",
        principal="Update dependencies and test: 1 week of work",
        created_date=datetime(2021, 1, 10),
        impact="Security vulnerabilities, compliance issues"
    )
    debt3.describe()


def demonstrate_architectural_smells():
    """Show architectural smells"""
    
    print("\n" + "="*70)
    print("ARCHITECTURAL SMELLS DETECTED")
    print("="*70)
    
    smell_catalog = {
        ArchitecturalSmell.GOD_COMPONENT: SmellDescription(
            name="God Component",
            description="A component that knows too much or does too much",
            symptoms=[
                "Component has many responsibilities",
                "Hard to understand and test",
                "Changes affect many parts of system",
                "High coupling with other components"
            ],
            causes=[
                "Lack of proper decomposition",
                "Feature creep over time",
                "No clear boundaries"
            ],
            solutions=[
                "Split into smaller components",
                "Apply Single Responsibility Principle",
                "Extract sub-components"
            ]
        ),
        
        ArchitecturalSmell.CIRCULAR_DEPENDENCY: SmellDescription(
            name="Circular Dependency",
            description="Components depend on each other in a cycle",
            symptoms=[
                "Component A depends on B, B depends on A",
                "Hard to test components in isolation",
                "Deployment order matters",
                "Changes ripple through cycle"
            ],
            causes=[
                "Poor component boundaries",
                "Shared concerns not extracted",
                "Tight coupling"
            ],
            solutions=[
                "Extract shared functionality",
                "Introduce dependency inversion",
                "Use events or callbacks"
            ]
        ),
        
        ArchitecturalSmell.SCATTERED_CONCERN: SmellDescription(
            name="Scattered Concern",
            description="A concern (like logging, security) is spread across many components",
            symptoms=[
                "Same code repeated in many places",
                "Changes require updates in many components",
                "Inconsistent implementation",
                "Hard to maintain"
            ],
            causes=[
                "No cross-cutting concern handling",
                "Copy-paste code",
                "No shared libraries"
            ],
            solutions=[
                "Extract to shared component",
                "Use aspect-oriented programming",
                "Create framework or library"
            ]
        )
    }
    
    for smell, description in smell_catalog.items():
        description.describe()


# ============================================================================
# KEY CONCEPTS
# ============================================================================

def show_key_concepts():
    """Show key concepts"""
    
    print("\n" + "="*70)
    print("KEY CONCEPTS: Decisions, Debt, and Smells")
    print("="*70)
    print("""
ARCHITECTURAL DECISIONS:
  • Should be documented (use ADRs)
  • Include context, decision, consequences, alternatives
  • Help future developers understand "why"
  • Can be superseded as system evolves
  
TECHNICAL DEBT:
  • Shortcuts taken for speed
  • Has "interest" (ongoing cost) and "principal" (fix cost)
  • Accumulates over time if not managed
  • Types: Architectural, Code, Test, Documentation, Dependency
  • Should be tracked and prioritized
  
ARCHITECTURAL SMELLS:
  • Warning signs of architectural problems
  • Indicate violations of good design principles
  • Examples: God Component, Circular Dependencies, Scattered Concerns
  • Should be identified and addressed
  
MANAGEMENT:
  • Document decisions as you make them
  • Track technical debt in backlog
  • Regularly refactor to pay down debt
  • Use code reviews to catch smells early
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demonstrate_architectural_decisions()
    demonstrate_technical_debt()
    demonstrate_architectural_smells()
    show_key_concepts()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Document architectural decisions using ADRs
✓ Technical debt has interest (ongoing cost) and principal (fix cost)
✓ Architectural smells indicate problems
✓ Manage debt by tracking and prioritizing
✓ Regular refactoring prevents debt accumulation
✓ Code reviews help catch smells early
    """)

