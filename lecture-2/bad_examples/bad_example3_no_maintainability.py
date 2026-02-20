#!/usr/bin/env python3
"""
BAD EXAMPLE 3: No Maintainability - Technical Debt Explosion

This demonstrates what happens when you DON't maintain your system.
Compare this to example5_maintainability.py to see the difference.

PROBLEMS:
1. Only fixes critical bugs (corrective only)
2. Ignores dependency updates (no adaptive)
3. No performance improvements (no perfective)
4. No refactoring (no preventive)
5. Technical debt accumulates
6. System becomes unmaintainable
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


# ============================================================================
# BAD: No maintainability - technical debt explosion
# ============================================================================

class UnmaintainableSystem:
    """
    BAD ARCHITECTURE: No maintainability strategy
    
    Problems:
    - Only fixes critical bugs
    - Ignores dependency updates
    - No performance improvements
    - No refactoring
    - Technical debt explodes
    - System becomes unmaintainable
    """
    
    def __init__(self):
        self.bug_count = 50  # Many bugs!
        self.technical_debt = 500.0  # High debt!
        self.performance_score = 0.60  # Poor performance
        self.maintainability_score = 0.30  # Hard to maintain
        self.dependency_version = "1.0.0"  # Old version!
        self.last_update = datetime.now() - timedelta(days=365)  # Year old!
        self.security_vulnerabilities = 12  # Many vulnerabilities!
        self.code_complexity = 45.0  # Very complex!
        self.test_coverage = 0.10  # Only 10%!
    
    def only_fix_critical_bugs(self, bug_description: str):
        """
        BAD: Only fix critical bugs, ignore others
        
        Problems:
        - Non-critical bugs accumulate
        - Bug count never decreases
        - Users frustrated with bugs
        - Technical debt increases
        """
        print(f"\n🐛 Bug report: {bug_description}")
        
        # Only fix if critical
        if "critical" in bug_description.lower() or "crash" in bug_description.lower():
            print("   ✅ Fixing critical bug...")
            self.bug_count = max(0, self.bug_count - 1)
            print(f"   📊 Remaining bugs: {self.bug_count}")
        else:
            print("   ⏭️  Bug deferred (not critical enough)")
            # Bug count stays the same or increases!
            self.bug_count += 1  # Actually increases!
            print(f"   📊 Bug count increased to: {self.bug_count}")
            print("   ⚠️  Technical debt increased!")
            self.technical_debt += 5.0
    
    def ignore_dependency_updates(self):
        """
        BAD: Ignore dependency updates
        
        Problems:
        - Security vulnerabilities accumulate
        - Compatibility issues
        - Missing features
        - Can't use new libraries
        """
        print("\n" + "=" * 70)
        print("DEPENDENCY UPDATE AVAILABLE")
        print("=" * 70)
        print(f"""
        ⚠️  New version available: 2.1.0
        ⚠️  Current version: {self.dependency_version} (outdated!)
        ⚠️  Security patches: 5 critical patches available
        ⚠️  Bug fixes: 12 bug fixes available
        ⚠️  New features: Performance improvements
        
        ❌ Decision: Ignore update (too risky to change)
        ❌ Result: Security vulnerabilities remain
        ❌ Result: Bugs remain unfixed
        ❌ Result: Missing performance improvements
        """)
        
        # Vulnerabilities accumulate
        self.security_vulnerabilities += 1
        print(f"   📊 Security vulnerabilities: {self.security_vulnerabilities}")
    
    def no_performance_improvements(self):
        """
        BAD: No performance improvements
        
        Problems:
        - Performance degrades over time
        - Users experience slowdowns
        - Can't handle growth
        - Technical debt increases
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE ISSUES REPORTED")
        print("=" * 70)
        print("""
        ⚠️  Users report: "System is slow"
        ⚠️  Response time: 2.5s (target: <1s)
        ⚠️  Throughput: 50 req/s (target: 200 req/s)
        
        ❌ Decision: No time for performance improvements
        ❌ Result: Performance degrades further
        ❌ Result: Users frustrated
        ❌ Result: Technical debt increases
        """)
        
        # Performance degrades
        self.performance_score = max(0, self.performance_score - 0.05)
        self.technical_debt += 10.0
        print(f"   📊 Performance score: {self.performance_score * 100:.0f}%")
        print(f"   📊 Technical debt: {self.technical_debt:.0f} hours")
    
    def no_refactoring(self):
        """
        BAD: No refactoring
        
        Problems:
        - Code complexity increases
        - Technical debt explodes
        - Can't add features
        - Can't fix bugs safely
        """
        print("\n" + "=" * 70)
        print("CODE QUALITY ISSUES")
        print("=" * 70)
        print(f"""
        ⚠️  Code complexity: {self.code_complexity} (target: <10)
        ⚠️  Technical debt: {self.technical_debt:.0f} hours
        ⚠️  Test coverage: {self.test_coverage * 100:.0f}% (target: >80%)
        ⚠️  Maintainability: {self.maintainability_score * 100:.0f}% (target: >80%)
        
        ❌ Decision: No time for refactoring (not urgent)
        ❌ Result: Code becomes unmaintainable
        ❌ Result: Can't add features
        ❌ Result: Can't fix bugs safely
        """)
        
        # Technical debt explodes
        self.technical_debt += 20.0
        self.code_complexity += 2.0
        self.maintainability_score = max(0, self.maintainability_score - 0.05)
        print(f"   📊 Technical debt: {self.technical_debt:.0f} hours")
        print(f"   📊 Code complexity: {self.code_complexity:.0f}")
        print(f"   📊 Maintainability: {self.maintainability_score * 100:.0f}%")
    
    def get_system_health(self):
        """Get system health (but it's terrible!)"""
        return {
            "bugs": self.bug_count,
            "technical_debt": f"{self.technical_debt:.0f} hours",
            "performance": f"{self.performance_score * 100:.0f}%",
            "maintainability": f"{self.maintainability_score * 100:.0f}%",
            "dependency_version": self.dependency_version,
            "security_vulnerabilities": self.security_vulnerabilities,
            "code_complexity": self.code_complexity,
            "test_coverage": f"{self.test_coverage * 100:.0f}%",
            "last_update": self.last_update.strftime("%Y-%m-%d")
        }


# ============================================================================
# DEMONSTRATION: Why This Is Bad
# ============================================================================

def demonstrate_no_maintainability():
    """
    Demonstrate the problems with no maintainability
    """
    print("=" * 70)
    print("BAD EXAMPLE 3: No Maintainability - Technical Debt Explosion")
    print("=" * 70)
    print("\n❌ PROBLEMS WITH NO MAINTAINABILITY:")
    print("   1. Only fixes critical bugs")
    print("   2. Ignores dependency updates")
    print("   3. No performance improvements")
    print("   4. No refactoring")
    print("   5. Technical debt explodes")
    print("   6. System becomes unmaintainable")
    
    system = UnmaintainableSystem()
    
    print("\n" + "=" * 70)
    print("INITIAL SYSTEM HEALTH")
    print("=" * 70)
    health = system.get_system_health()
    for key, value in health.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    print("SIMULATING 6 MONTHS OF POOR MAINTENANCE")
    print("=" * 70)
    
    # Simulate 6 months
    for month in range(6):
        print(f"\n📅 Month {month + 1}:")
        
        # Only fix critical bugs
        system.only_fix_critical_bugs("Critical: System crash on startup")
        system.only_fix_critical_bugs("Minor: UI typo")
        system.only_fix_critical_bugs("Medium: Slow search")
        
        # Ignore dependency updates
        system.ignore_dependency_updates()
        
        # No performance improvements
        system.no_performance_improvements()
        
        # No refactoring
        system.no_refactoring()
    
    print("\n" + "=" * 70)
    print("SYSTEM HEALTH AFTER 6 MONTHS")
    print("=" * 70)
    health = system.get_system_health()
    for key, value in health.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    print("SCENARIO: Try to Add New Feature")
    print("=" * 70)
    print("""
    Product manager: "We need to add payment integration"
    
    With this system:
    1. Code is too complex to understand
    2. No tests to verify changes
    3. Technical debt makes changes risky
    4. Can't add feature without breaking things
    5. Takes 3 months instead of 2 weeks
    
    Result: Feature delayed, costs explode, users frustrated!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: Security Vulnerability Found")
    print("=" * 70)
    print("""
    Security team: "Critical vulnerability in dependency"
    
    With this system:
    1. Dependency is 2 years old
    2. Can't update (too risky)
    3. Must patch manually (expensive)
    4. Might break existing code
    5. Takes weeks to fix
    
    Result: System vulnerable, compliance issues, potential breach!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: Performance Issues")
    print("=" * 70)
    print("""
    Users: "System is too slow, we're leaving"
    
    With this system:
    1. Performance degraded over time
    2. Code is too complex to optimize
    3. No tests to verify optimizations
    4. Can't improve without breaking things
    5. Must rewrite to fix
    
    Result: Users leave, revenue lost, must rewrite!
    """)
    
    print("\n" + "=" * 70)
    print("COMPARE TO: Good Maintainability (example5_maintainability.py)")
    print("=" * 70)
    print("""
    With good maintainability:
    
    ✅ Corrective: Fix bugs regularly
    ✅ Adaptive: Update dependencies monthly
    ✅ Perfective: Improve performance quarterly
    ✅ Preventive: Refactor regularly
    
    Result:
    • 5 bugs (vs 50+)
    • 20 hours debt (vs 500+)
    • 90% performance (vs 60%)
    • 85% maintainability (vs 30%)
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD IMPACT")
    print("=" * 70)
    print("""
    Company with no maintainability:
    
    After 1 year:
    • 50+ bugs (vs 5)
    • 500+ hours debt (vs 20)
    • 60% performance (vs 90%)
    • 30% maintainability (vs 85%)
    • 12 security vulnerabilities
    • Can't add features
    • Must rewrite system
    
    Cost:
    • $500k+ in lost productivity
    • $200k+ in security incidents
    • $1M+ to rewrite system
    • Lost revenue from poor performance
    • Customer churn
    
    With maintainability:
    • System stays healthy
    • Can add features quickly
    • Low technical debt
    • Good performance
    • Secure and up-to-date
    """)


if __name__ == "__main__":
    demonstrate_no_maintainability()


