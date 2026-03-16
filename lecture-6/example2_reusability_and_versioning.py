#!/usr/bin/env python3
"""
Example 2: Reusability, Library vs Framework, Interface Evolution

This example demonstrates:
- Component Reusability: design for use in multiple contexts
- Library vs Framework: library = you call it; framework = it calls you
- Interface Evolution: adding optional params, deprecation, compatibility
- Versioning Strategies: semantic versioning, backward compatibility

Key Concept: Reusable components need stable interfaces and clear versioning.

Reference: Chapter 6 - Reusability and Interfaces
"""

from typing import List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings


# ============================================================================
# LIBRARY vs FRAMEWORK
# ============================================================================

# --- LIBRARY: You control the flow, you call the library ---

class ValidationLibrary:
    """
    Library: exposes functions; caller decides when and how to use them.
    Reusable in any flow (web request, CLI, batch).
    """
    
    @staticmethod
    def is_valid_email(s: str) -> bool:
        return "@" in s and "." in s and len(s) > 5
    
    @staticmethod
    def is_valid_length(s: str, min_len: int = 1, max_len: int = 1000) -> bool:
        return min_len <= len(s) <= max_len


# --- FRAMEWORK: Framework controls the flow, calls your code ---

class Handler(ABC):
    """Your code: framework calls handle() when event occurs."""
    
    @abstractmethod
    def handle(self, event: dict) -> Optional[dict]:
        """Process event. Return response or None."""
        pass


class SimpleEventFramework:
    """
    Minimal framework: you register handlers; framework invokes them.
    Framework controls flow (event loop); you supply handlers.
    """
    
    def __init__(self) -> None:
        self._handlers: List[Callable[[dict], Optional[dict]]] = []
    
    def register(self, handler: Callable[[dict], Optional[dict]]) -> None:
        self._handlers.append(handler)
    
    def run(self, event: dict) -> List[dict]:
        """Framework runs: calls each handler."""
        results = []
        for h in self._handlers:
            r = h(event)
            if r is not None:
                results.append(r)
        return results


# ============================================================================
# INTERFACE EVOLUTION: Adding features without breaking clients
# ============================================================================

class ILogger(ABC):
    """Original interface: single method."""
    
    @abstractmethod
    def log(self, message: str) -> None:
        pass


class ILoggerV2(ABC):
    """
    Evolved interface: add optional parameters with defaults.
    Backward compatible: existing log(message) still works.
    """
    
    @abstractmethod
    def log(
        self,
        message: str,
        level: str = "info",
        metadata: Optional[dict] = None,
    ) -> None:
        pass


class SimpleLogger(ILoggerV2):
    """Implements evolved interface; supports old and new call styles."""
    
    def log(
        self,
        message: str,
        level: str = "info",
        metadata: Optional[dict] = None,
    ) -> None:
        prefix = f"[{level.upper()}]"
        extra = f" {metadata}" if metadata else ""
        print(f"{prefix} {message}{extra}")


# ============================================================================
# DEPRECATION: Phasing out old API
# ============================================================================

class ConfigReader:
    """
    Versioned API: old method deprecated, new method preferred.
    Deprecation warnings guide clients to migrate.
    """
    
    def get_value(self, key: str) -> Optional[str]:
        """Preferred: use get(key) or get(key, default)."""
        return self.get(key)
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Current API."""
        # Simulate reading config
        return {"host": "localhost", "port": "8080"}.get(key, default)
    
    def read_value(self, key: str) -> Optional[str]:
        """Deprecated: use get(key) instead."""
        warnings.warn(
            "read_value is deprecated; use get(key) instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get(key)


# ============================================================================
# VERSIONING: Semantic versioning and compatibility
# ============================================================================

@dataclass
class ApiVersion:
    """Semantic versioning: MAJOR.MINOR.PATCH."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"
    
    def backward_compatible_with(self, other: "ApiVersion") -> bool:
        """Same major = backward compatible."""
        return self.major == other.major
    
    def compatible_version(self) -> str:
        """Explain compatibility."""
        return f"Compatible with any {self.major}.x.x"


class VersionedClient:
    """
    Client that declares required API version.
    Server can support multiple versions for evolution.
    """
    
    def __init__(self, api_version: ApiVersion) -> None:
        self.api_version = api_version
    
    def request(self, path: str) -> str:
        """Send request with version header."""
        return f"GET {path} [Accept: api/{self.api_version}]"


# ============================================================================
# REUSABILITY: One component, many contexts
# ============================================================================

class JsonSerializer:
    """
    Reusable component: no dependency on web, CLI, or batch.
    Single responsibility; used by different systems.
    """
    
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)
    
    def deserialize(self, text: str) -> dict:
        import json
        return json.loads(text)


def demonstrate_reusability() -> None:
    print("\n" + "="*70)
    print("LIBRARY vs FRAMEWORK")
    print("="*70)
    
    # Library: you call it
    lib = ValidationLibrary()
    print("Library (you call it):")
    print("  is_valid_email('a@b.co'):", lib.is_valid_email("a@b.co"))
    
    # Framework: it calls you
    fw = SimpleEventFramework()
    fw.register(lambda e: {"echo": e.get("msg")})
    results = fw.run({"msg": "hello"})
    print("Framework (it calls you):")
    print("  run({msg: 'hello'}):", results)
    
    print("\n" + "="*70)
    print("INTERFACE EVOLUTION")
    print("="*70)
    
    logger = SimpleLogger()
    logger.log("Started")                    # Old style
    logger.log("Done", level="info")         # New style
    logger.log("Error", level="error", metadata={"code": 500})
    
    print("\nDeprecation:")
    reader = ConfigReader()
    print("  get('host'):", reader.get("host"))
    # reader.read_value("host")  # Would emit DeprecationWarning
    
    print("\n" + "="*70)
    print("VERSIONING")
    print("="*70)
    
    v1 = ApiVersion(1, 2, 3)
    v2 = ApiVersion(2, 0, 0)
    print(f"  {v1} backward_compatible with {v2}?", v1.backward_compatible_with(v2))
    print(f"  {v1}.compatible_version():", v1.compatible_version())
    
    client = VersionedClient(ApiVersion(1, 0, 0))
    print("  VersionedClient request:", client.request("/users"))
    
    print("\n" + "="*70)
    print("KEY CONCEPTS")
    print("="*70)
    print("""
LIBRARY vs FRAMEWORK:
  • Library: You control flow; you call library functions
  • Framework: Framework controls flow; you plug in handlers
  • Both are reusable; choice depends on who owns the control flow

INTERFACE EVOLUTION:
  • Add optional parameters with defaults (backward compatible)
  • Deprecate old methods; warn, then remove in next major version
  • Document migration path

VERSIONING (Semantic Versioning):
  • MAJOR: Breaking changes
  • MINOR: New features, backward compatible
  • PATCH: Bug fixes, backward compatible
  • Same major = clients can upgrade without code change

REUSABILITY:
  • Design for multiple contexts (web, CLI, batch)
  • Avoid context-specific dependencies in the interface
  • Stable, minimal interface increases reuse
    """)


if __name__ == "__main__":
    demonstrate_reusability()
