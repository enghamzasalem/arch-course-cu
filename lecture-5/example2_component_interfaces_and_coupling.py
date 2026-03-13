#!/usr/bin/env python3
"""
Example 2: Component Interfaces, Cohesion and Coupling

This example demonstrates:
- Component Interfaces: Clear contracts between components
- Module Cohesion: How closely related elements within a component are
- Module Coupling: How dependent components are on each other
- Design for: High cohesion, Low coupling
- Component lifecycle and dependency injection

Key Concept: Good modular design = High cohesion + Low coupling.

Reference: Chapter 5 - Modularity and Components
"""

from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
# ============================================================================
# BUSINESS SCENARIO: Document Management System
# ============================================================================
# Components: DocumentStore, SearchEngine, Renderer
# Interfaces define contracts; implementations can vary
# Low coupling: components depend on interfaces, not concrete implementations


# ============================================================================
# INTERFACES (Contracts - Low Coupling)
# ============================================================================

class IDocumentStorage(Protocol):
    """Interface: Components depend on this, not concrete storage."""
    
    def save(self, doc_id: str, content: str) -> bool: ...
    def load(self, doc_id: str) -> Optional[str]: ...
    def delete(self, doc_id: str) -> bool: ...
    def list_ids(self) -> List[str]: ...


class ISearchIndex(Protocol):
    """Interface: Search depends on index contract."""
    
    def index(self, doc_id: str, content: str) -> None: ...
    def search(self, query: str) -> List[str]: ...
    def remove(self, doc_id: str) -> None: ...


# ============================================================================
# IMPLEMENTATIONS (Can be swapped - Low Coupling)
# ============================================================================

class InMemoryDocumentStore:
    """Concrete storage - implements IDocumentStorage."""
    
    def __init__(self):
        self._docs: Dict[str, str] = {}
    
    def save(self, doc_id: str, content: str) -> bool:
        self._docs[doc_id] = content
        return True
    
    def load(self, doc_id: str) -> Optional[str]:
        return self._docs.get(doc_id)
    
    def delete(self, doc_id: str) -> bool:
        if doc_id in self._docs:
            del self._docs[doc_id]
            return True
        return False
    
    def list_ids(self) -> List[str]:
        return list(self._docs.keys())


class SimpleSearchIndex:
    """Concrete search - implements ISearchIndex."""
    
    def __init__(self):
        self._index: Dict[str, List[str]] = {}
    
    def index(self, doc_id: str, content: str) -> None:
        words = content.lower().split()
        for word in words:
            if word not in self._index:
                self._index[word] = []
            if doc_id not in self._index[word]:
                self._index[word].append(doc_id)
    
    def search(self, query: str) -> List[str]:
        words = query.lower().split()
        if not words:
            return []
        # Simple: docs containing any query word
        result = set()
        for word in words:
            result.update(self._index.get(word, []))
        return list(result)
    
    def remove(self, doc_id: str) -> None:
        for word in list(self._index.keys()):
            self._index[word] = [d for d in self._index[word] if d != doc_id]


# ============================================================================
# HIGH COHESION COMPONENT: DocumentManager
# ============================================================================
# Cohesion: All operations are about document lifecycle
# Single concern: Manage documents (save, load, search)


class DocumentManager:
    """
    HIGH COHESION: All methods relate to document management.
    LOW COUPLING: Depends on interfaces (IDocumentStorage, ISearchIndex).
    """
    
    def __init__(
        self,
        storage: IDocumentStorage,
        search_index: ISearchIndex,
    ):
        self._storage = storage
        self._search = search_index
    
    def create_document(self, doc_id: str, content: str) -> bool:
        """Create and index a document."""
        if self._storage.save(doc_id, content):
            self._search.index(doc_id, content)
            return True
        return False
    
    def get_document(self, doc_id: str) -> Optional[str]:
        """Retrieve document by ID."""
        return self._storage.load(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and remove from index."""
        if self._storage.delete(doc_id):
            self._search.remove(doc_id)
            return True
        return False
    
    def search_documents(self, query: str) -> List[str]:
        """Search documents by query."""
        return self._search.search(query)


# ============================================================================
# COUPLING ANALYSIS
# ============================================================================

def analyze_coupling():
    """Demonstrate coupling levels."""
    
    print("\n" + "="*70)
    print("COUPLING AND COHESION ANALYSIS")
    print("="*70)
    
    print("""
TIGHT COUPLING (Bad):
  • DocumentManager directly instantiates InMemoryDocumentStore
  • Cannot swap storage without changing DocumentManager
  • Hard to test (cannot mock storage)

LOOSE COUPLING (Good):
  • DocumentManager receives storage via constructor (Dependency Injection)
  • Depends on IDocumentStorage interface, not concrete class
  • Can swap: InMemoryDocumentStore, FileDocumentStore, S3DocumentStore
  • Easy to test: inject mock storage

COHESION TYPES (from low to high):
  • Coincidental: Parts unrelated (bad)
  • Logical: Same category but different operations
  • Temporal: Same time (e.g., startup)
  • Procedural: Same algorithm/flow
  • Communicational: Same data
  • Sequential: Output of one is input of next
  • Functional: Single well-defined purpose (best)

GOAL: High functional cohesion, Low coupling
    """)


# ============================================================================
# COMPONENT LIFECYCLE
# ============================================================================

@dataclass
class ComponentLifecycle:
    """Component lifecycle stages."""
    name: str
    stages: List[str]
    
    def describe(self):
        print(f"\n{self.name}:")
        for i, stage in enumerate(self.stages, 1):
            print(f"  {i}. {stage}")


def show_component_lifecycle():
    """Show component lifecycle."""
    
    print("\n" + "="*70)
    print("COMPONENT LIFECYCLE")
    print("="*70)
    
    lifecycle = ComponentLifecycle(
        "Typical Component Lifecycle",
        [
            "Creation: Component instantiated",
            "Initialization: Dependencies injected, config loaded",
            "Active: Processing requests, serving clients",
            "Update: New version deployed (if replaceable)",
            "Disposal: Cleanup, release resources",
        ]
    )
    lifecycle.describe()
    
    print("""
DESIGN FOR LIFECYCLE:
  • Lazy initialization: Create when needed
  • Graceful shutdown: Handle termination signals
  • Stateless when possible: Easier to replace/scale
  • Dependency injection: Enables swapping implementations
    """)


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_interfaces_and_coupling():
    """Demonstrate interface-based design."""
    
    print("\n" + "="*70)
    print("EXAMPLE: Document Manager with Interface-Based Design")
    print("="*70)
    
    # Inject dependencies - can swap implementations
    storage = InMemoryDocumentStore()
    search = SimpleSearchIndex()
    manager = DocumentManager(storage=storage, search_index=search)
    
    # Use
    manager.create_document("doc-1", "Python programming language tutorial")
    manager.create_document("doc-2", "Java and Python comparison")
    manager.create_document("doc-3", "Database design patterns")
    
    print("\nDocuments created: doc-1, doc-2, doc-3")
    
    print("\nSearch 'python':", manager.search_documents("python"))
    print("Search 'database':", manager.search_documents("database"))
    
    doc = manager.get_document("doc-1")
    print(f"\nGet doc-1: {doc[:40]}..." if doc else "Not found")
    
    manager.delete_document("doc-2")
    print("\nDeleted doc-2. Search 'java':", manager.search_documents("java"))
    
    analyze_coupling()
    show_component_lifecycle()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
✓ Component Interfaces: Define contracts, enable swapping
✓ Low Coupling: Depend on interfaces, inject implementations
✓ High Cohesion: Each component has single, clear purpose
✓ Dependency Injection: Enables testing and flexibility
✓ Component Lifecycle: Design for creation, use, replacement
✓ Protocol/ABC: Python way to define interfaces
    """)


if __name__ == "__main__":
    demonstrate_interfaces_and_coupling()
