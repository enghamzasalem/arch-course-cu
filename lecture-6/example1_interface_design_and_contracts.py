#!/usr/bin/env python3
"""
Example 1: Interface Design Principles and API Contracts

This example demonstrates:
- Interface Design Principles: minimal, stable, clear contracts
- Abstraction and Information Hiding: expose what, hide how
- Interface Contracts: preconditions, postconditions, invariants
- API Design: consistency, discoverability, backward compatibility

Key Concept: Good interfaces are minimal, stable, and hide implementation details.

Reference: Chapter 6 - Reusability and Interfaces
"""

from typing import List, Optional, Protocol, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod


# ============================================================================
# BUSINESS SCENARIO: Caching Service
# ============================================================================
# Multiple consumers need caching; interface must be reusable across contexts
# (web app, CLI, batch job) and implementations (memory, Redis, file)


# ============================================================================
# INTERFACE DESIGN: Minimal, Stable, Clear
# ============================================================================

class ICache(Protocol):
    """
    Minimal interface: only what clients need.
    Stable: avoid adding/removing methods frequently.
    Clear: names and behavior are unambiguous.
    """
    
    def get(self, key: str) -> Optional[bytes]:
        """Return value for key, or None if missing/expired."""
        ...
    
    def set(self, key: str, value: bytes, ttl_seconds: Optional[int] = None) -> None:
        """Store value for key. Optional TTL in seconds."""
        ...
    
    def delete(self, key: str) -> bool:
        """Remove key. Return True if key existed."""
        ...


# Contract (documented):
# - get: key must be non-empty str; returns None only when key absent/expired
# - set: key non-empty; ttl_seconds None means no expiry
# - delete: key must be non-empty; idempotent for missing key (returns False)


# ============================================================================
# IMPLEMENTATIONS: Same interface, different strategies
# ============================================================================

class InMemoryCache:
    """Reusable implementation: in-memory cache."""
    
    def __init__(self) -> None:
        self._store: Dict[str, bytes] = {}
    
    def get(self, key: str) -> Optional[bytes]:
        if not key:
            raise ValueError("key must be non-empty")
        return self._store.get(key)
    
    def set(self, key: str, value: bytes, ttl_seconds: Optional[int] = None) -> None:
        if not key:
            raise ValueError("key must be non-empty")
        self._store[key] = value
        # Ignore ttl for simplicity in this example
    
    def delete(self, key: str) -> bool:
        if not key:
            raise ValueError("key must be non-empty")
        if key in self._store:
            del self._store[key]
            return True
        return False


class PrefixCache:
    """
    Reusable wrapper: adds key prefix (namespace).
    Same ICache interface - clients don't know about prefix.
    """
    
    def __init__(self, delegate: ICache, prefix: str) -> None:
        self._delegate = delegate
        self._prefix = f"{prefix}:"
    
    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"
    
    def get(self, key: str) -> Optional[bytes]:
        return self._delegate.get(self._key(key))
    
    def set(self, key: str, value: bytes, ttl_seconds: Optional[int] = None) -> None:
        self._delegate.set(self._key(key), value, ttl_seconds)
    
    def delete(self, key: str) -> bool:
        return self._delegate.delete(self._key(key))


# ============================================================================
# INTERFACE CONTRACTS: Explicit preconditions/postconditions
# ============================================================================

@dataclass
class CacheContract:
    """
    Documented contract for ICache.
    Preconditions: what must hold before call.
    Postconditions: what holds after successful call.
    """
    get_pre = "key is non-empty string"
    get_post = "returns value or None; does not throw for missing key"
    
    set_pre = "key is non-empty string, value is bytes"
    set_post = "key maps to value; optional TTL applied"
    
    delete_pre = "key is non-empty string"
    delete_post = "key removed; True iff key existed"


# ============================================================================
# API DESIGN: Consistency and discoverability
# ============================================================================

class CacheFactory:
    """
    Factory with consistent naming: create_* for implementations.
    Hides construction details; returns ICache.
    """
    
    @staticmethod
    def create_memory() -> ICache:
        return InMemoryCache()
    
    @staticmethod
    def create_namespaced(base: ICache, namespace: str) -> ICache:
        return PrefixCache(base, namespace)


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_interface_design() -> None:
    print("\n" + "="*70)
    print("INTERFACE DESIGN: Caching Service")
    print("="*70)
    
    cache: ICache = InMemoryCache()
    cache.set("user:1", b'{"name": "Alice"}')
    cache.set("user:2", b'{"name": "Bob"}')
    
    print("\n1. InMemoryCache (implements ICache):")
    print("   get('user:1'):", cache.get("user:1"))
    print("   get('missing'):", cache.get("missing"))
    
    base = InMemoryCache()
    ns_cache: ICache = PrefixCache(base, "api")
    ns_cache.set("req:1", b"response body")
    
    print("\n2. PrefixCache (same ICache, different namespace):")
    print("   ns_cache.get('req:1'):", ns_cache.get("req:1"))
    print("   base.get('api:req:1'):", base.get("api:req:1"))
    
    print("\n3. Contract summary:")
    print("   get  - pre:", CacheContract.get_pre)
    print("        post:", CacheContract.get_post)
    print("   set  - pre:", CacheContract.set_pre)
    print("   delete - pre:", CacheContract.delete_pre)
    
    print("\n" + "="*70)
    print("KEY PRINCIPLES")
    print("="*70)
    print("""
INTERFACE DESIGN:
  • Minimal: Only methods clients need (get, set, delete)
  • Stable: Avoid breaking changes; extend with optional params
  • Clear: Same naming (get/set/delete), same semantics across impls

CONTRACTS:
  • Preconditions: What must be true before call (e.g. non-empty key)
  • Postconditions: What is true after (e.g. key removed)
  • Document and enforce in implementation

REUSABILITY:
  • ICache used by web app, CLI, batch job
  • InMemoryCache and PrefixCache interchangeable where ICache expected
  • Factory hides construction; returns interface type
    """)


if __name__ == "__main__":
    demonstrate_interface_design()
