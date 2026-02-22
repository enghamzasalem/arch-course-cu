#!/usr/bin/env python3
"""
Example 5: Maintainability - Four Types of Maintenance

This example demonstrates:
- Corrective Maintenance: Fix bugs and defects
- Adaptive Maintenance: Adapt to external changes
- Perfective Maintenance: Improve external qualities
- Preventive Maintenance: Improve internal qualities

Key Concept: Maintenance is not just bug fixing. It includes adapting
to changes, improving quality, and preventing future problems.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time


# ============================================================================
# BUSINESS SCENARIO: Legacy System Evolution
# ============================================================================
# A system needs different types of maintenance to remain viable:
# - Corrective: Fix bugs users report
# - Adaptive: Update for new OS/library versions
# - Perfective: Improve performance and features
# - Preventive: Refactor to reduce technical debt
#


class MaintenanceType(Enum):
    """Types of maintenance"""
    CORRECTIVE = "corrective"  # Fix bugs
    ADAPTIVE = "adaptive"  # Adapt to external changes
    PERFECTIVE = "perfective"  # Improve external qualities
    PREVENTIVE = "preventive"  # Improve internal qualities


@dataclass
class MaintenanceTask:
    """A maintenance task"""
    type: MaintenanceType
    description: str
    priority: int  # 1-5, 5 is highest
    estimated_hours: float
    completed: bool = False
    completed_date: Optional[datetime] = None


@dataclass
class SystemHealth:
    """System health metrics"""
    bug_count: int
    technical_debt_hours: float
    performance_score: float  # 0-1
    maintainability_score: float  # 0-1
    external_dependency_version: str
    last_update: datetime


# ============================================================================
# SYSTEM WITH PROPER MAINTENANCE
# ============================================================================

class WellMaintainedSystem:
    """
    System with proper maintenance strategy.
    
    Maintenance Strategy:
    ✅ Corrective: Fix bugs quickly
    ✅ Adaptive: Keep dependencies updated
    ✅ Perfective: Continuously improve
    ✅ Preventive: Regular refactoring
    """
    
    def __init__(self):
        self.health = SystemHealth(
            bug_count=5,
            technical_debt_hours=20.0,
            performance_score=0.90,
            maintainability_score=0.85,
            external_dependency_version="2.1.0",
            last_update=datetime.now()
        )
        self.maintenance_history: List[MaintenanceTask] = []
        self.total_maintenance_hours = 0.0
    
    def corrective_maintenance(self, bug_description: str, priority: int = 3):
        """Corrective maintenance: Fix bugs"""
        print("\n" + "=" * 70)
        print("CORRECTIVE MAINTENANCE: Fixing Bugs")
        print("=" * 70)
        print(f"\n🐛 Bug: {bug_description}")
        print(f"   Priority: {priority}/5")
        
        task = MaintenanceTask(
            type=MaintenanceType.CORRECTIVE,
            description=bug_description,
            priority=priority,
            estimated_hours=4.0 if priority >= 4 else 2.0
        )
        
        print(f"   Estimated time: {task.estimated_hours} hours")
        print("   ✅ Bug fixed and tested")
        
        task.completed = True
        task.completed_date = datetime.now()
        self.maintenance_history.append(task)
        self.total_maintenance_hours += task.estimated_hours
        
        # Reduce bug count
        self.health.bug_count = max(0, self.health.bug_count - 1)
        
        print(f"   📊 Remaining bugs: {self.health.bug_count}")
        return task
    
    def adaptive_maintenance(self, change_description: str):
        """Adaptive maintenance: Adapt to external changes"""
        print("\n" + "=" * 70)
        print("ADAPTIVE MAINTENANCE: Adapting to External Changes")
        print("=" * 70)
        print(f"\n🔄 Change: {change_description}")
        
        task = MaintenanceTask(
            type=MaintenanceType.ADAPTIVE,
            description=change_description,
            priority=4,  # Usually high priority
            estimated_hours=8.0
        )
        
        print(f"   Estimated time: {task.estimated_hours} hours")
        print("   ✅ System adapted to new version")
        print("   ✅ Tests updated and passing")
        print("   ✅ Backward compatibility maintained")
        
        task.completed = True
        task.completed_date = datetime.now()
        self.maintenance_history.append(task)
        self.total_maintenance_hours += task.estimated_hours
        
        # Update dependency version
        version_parts = self.health.external_dependency_version.split('.')
        new_minor = int(version_parts[1]) + 1
        self.health.external_dependency_version = f"{version_parts[0]}.{new_minor}.0"
        self.health.last_update = datetime.now()
        
        print(f"   📊 Dependency version: {self.health.external_dependency_version}")
        return task
    
    def perfective_maintenance(self, improvement_description: str):
        """Perfective maintenance: Improve external qualities"""
        print("\n" + "=" * 70)
        print("PERFECTIVE MAINTENANCE: Improving External Qualities")
        print("=" * 70)
        print(f"\n✨ Improvement: {improvement_description}")
        
        task = MaintenanceTask(
            type=MaintenanceType.PERFECTIVE,
            description=improvement_description,
            priority=3,
            estimated_hours=16.0
        )
        
        print(f"   Estimated time: {task.estimated_hours} hours")
        print("   ✅ Performance improved")
        print("   ✅ User experience enhanced")
        print("   ✅ New features added")
        
        task.completed = True
        task.completed_date = datetime.now()
        self.maintenance_history.append(task)
        self.total_maintenance_hours += task.estimated_hours
        
        # Improve performance
        self.health.performance_score = min(1.0, self.health.performance_score + 0.05)
        
        print(f"   📊 Performance score: {self.health.performance_score * 100:.0f}%")
        return task
    
    def preventive_maintenance(self, refactoring_description: str):
        """Preventive maintenance: Improve internal qualities"""
        print("\n" + "=" * 70)
        print("PREVENTIVE MAINTENANCE: Improving Internal Qualities")
        print("=" * 70)
        print(f"\n🔧 Refactoring: {refactoring_description}")
        
        task = MaintenanceTask(
            type=MaintenanceType.PREVENTIVE,
            description=refactoring_description,
            priority=2,  # Often lower priority (but important!)
            estimated_hours=12.0
        )
        
        print(f"   Estimated time: {task.estimated_hours} hours")
        print("   ✅ Code refactored")
        print("   ✅ Technical debt reduced")
        print("   ✅ Maintainability improved")
        print("   ✅ Tests updated")
        
        task.completed = True
        task.completed_date = datetime.now()
        self.maintenance_history.append(task)
        self.total_maintenance_hours += task.estimated_hours
        
        # Reduce technical debt
        self.health.technical_debt_hours = max(0, self.health.technical_debt_hours - 10.0)
        self.health.maintainability_score = min(1.0, self.health.maintainability_score + 0.05)
        
        print(f"   📊 Technical debt: {self.health.technical_debt_hours} hours")
        print(f"   📊 Maintainability: {self.health.maintainability_score * 100:.0f}%")
        return task
    
    def get_maintenance_report(self) -> Dict:
        """Get maintenance report"""
        by_type = {}
        for maint_type in MaintenanceType:
            tasks = [t for t in self.maintenance_history if t.type == maint_type]
            by_type[maint_type.value] = {
                "count": len(tasks),
                "total_hours": sum(t.estimated_hours for t in tasks)
            }
        
        return {
            "health": {
                "bugs": self.health.bug_count,
                "technical_debt": f"{self.health.technical_debt_hours} hours",
                "performance": f"{self.health.performance_score * 100:.0f}%",
                "maintainability": f"{self.health.maintainability_score * 100:.0f}%",
                "dependency_version": self.health.external_dependency_version
            },
            "maintenance": by_type,
            "total_hours": self.total_maintenance_hours
        }


# ============================================================================
# SYSTEM WITH POOR MAINTENANCE
# ============================================================================

class PoorlyMaintainedSystem:
    """
    System with poor maintenance strategy.
    
    Problems:
    ❌ Only fixes critical bugs (corrective only)
    ❌ Ignores dependency updates (no adaptive)
    ❌ No performance improvements (no perfective)
    ❌ No refactoring (no preventive)
    ❌ Technical debt accumulates
    """
    
    def __init__(self):
        self.health = SystemHealth(
            bug_count=47,  # Many bugs!
            technical_debt_hours=500.0,  # High debt!
            performance_score=0.65,  # Poor performance
            maintainability_score=0.35,  # Hard to maintain
            external_dependency_version="1.0.0",  # Old version!
            last_update=datetime.now() - timedelta(days=365)  # Year old!
        )
        self.maintenance_history: List[MaintenanceTask] = []
        self.total_maintenance_hours = 0.0
    
    def only_fix_critical_bugs(self, bug_description: str):
        """Only fix critical bugs - ignore others"""
        print(f"\n🐛 Critical bug: {bug_description}")
        print("   ⚠️  Only fixing critical bugs...")
        print("   ❌ Ignoring non-critical bugs")
        
        # Only fix if critical
        if "critical" in bug_description.lower() or "crash" in bug_description.lower():
            self.health.bug_count = max(0, self.health.bug_count - 1)
            print("   ✅ Critical bug fixed")
        else:
            print("   ⏭️  Bug deferred (not critical)")
            # Bug count stays the same or increases!
    
    def ignore_dependency_updates(self):
        """Ignore dependency updates"""
        print("\n⚠️  New dependency version available: 2.1.0")
        print("   ❌ Ignoring update (too risky)")
        print("   ⚠️  Running on outdated version: 1.0.0")
        print("   ⚠️  Security vulnerabilities may exist")
    
    def no_performance_improvements(self):
        """No performance improvements"""
        print("\n⚠️  Performance issues reported by users")
        print("   ❌ No time for performance improvements")
        print("   ⚠️  Performance degrades over time")
        self.health.performance_score = max(0, self.health.performance_score - 0.01)
    
    def no_refactoring(self):
        """No refactoring"""
        print("\n⚠️  Code becoming hard to maintain")
        print("   ❌ No time for refactoring")
        print("   ⚠️  Technical debt accumulating")
        self.health.technical_debt_hours += 10.0
        self.health.maintainability_score = max(0, self.health.maintainability_score - 0.01)


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_maintainability():
    """
    Demonstrate the four types of maintenance.
    """
    print("=" * 70)
    print("EXAMPLE 5: Maintainability - Four Types of Maintenance")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Corrective: Fix bugs and defects")
    print("   • Adaptive: Adapt to external changes")
    print("   • Perfective: Improve external qualities")
    print("   • Preventive: Improve internal qualities")
    
    # Well-maintained system
    print("\n" + "=" * 70)
    print("WELL-MAINTAINED SYSTEM")
    print("=" * 70)
    
    good_system = WellMaintainedSystem()
    
    # Simulate maintenance over 6 months
    print("\n📅 Simulating 6 months of maintenance...")
    
    # Corrective maintenance
    good_system.corrective_maintenance("Payment processing error", priority=5)
    good_system.corrective_maintenance("UI display bug", priority=2)
    good_system.corrective_maintenance("Database query timeout", priority=4)
    
    # Adaptive maintenance
    good_system.adaptive_maintenance("Update to Python 3.11")
    good_system.adaptive_maintenance("Update database driver to latest version")
    
    # Perfective maintenance
    good_system.perfective_maintenance("Optimize search performance")
    good_system.perfective_maintenance("Add caching layer")
    
    # Preventive maintenance
    good_system.preventive_maintenance("Refactor payment module")
    good_system.preventive_maintenance("Reduce code duplication")
    
    # Report
    print("\n" + "=" * 70)
    print("MAINTENANCE REPORT")
    print("=" * 70)
    report = good_system.get_maintenance_report()
    
    print("\n📊 System Health:")
    for key, value in report["health"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n📊 Maintenance by Type:")
    for maint_type, stats in report["maintenance"].items():
        print(f"   {maint_type.title()}: {stats['count']} tasks, {stats['total_hours']:.0f} hours")
    
    print(f"\n⏱️  Total Maintenance Time: {report['total_hours']:.0f} hours")
    
    # Poorly maintained system
    print("\n" + "=" * 70)
    print("POORLY-MAINTAINED SYSTEM")
    print("=" * 70)
    
    bad_system = PoorlyMaintainedSystem()
    
    print("\n📅 Simulating 6 months of poor maintenance...")
    
    bad_system.only_fix_critical_bugs("Critical: System crash on startup")
    bad_system.only_fix_critical_bugs("Minor: UI typo")
    bad_system.ignore_dependency_updates()
    bad_system.no_performance_improvements()
    bad_system.no_refactoring()
    
    print("\n📊 System Health:")
    print(f"   Bugs: {bad_system.health.bug_count}")
    print(f"   Technical Debt: {bad_system.health.technical_debt_hours} hours")
    print(f"   Performance: {bad_system.health.performance_score * 100:.0f}%")
    print(f"   Maintainability: {bad_system.health.maintainability_score * 100:.0f}%")
    print(f"   Dependency Version: {bad_system.health.external_dependency_version} (outdated!)")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Four Types of Maintenance:
    
    1. Corrective Maintenance:
       • Fix bugs and defects
       • Goal: Decrease bug count
       • Priority: Usually high
       • Example: Fix payment processing error
    
    2. Adaptive Maintenance:
       • Adapt to external changes
       • Goal: Keep system compatible
       • Priority: Usually high
       • Example: Update to new OS/library version
    
    3. Perfective Maintenance:
       • Improve external qualities
       • Goal: Enhance user experience
       • Priority: Medium
       • Example: Improve performance, add features
    
    4. Preventive Maintenance:
       • Improve internal qualities
       • Goal: Reduce technical debt
       • Priority: Often low (but important!)
       • Example: Refactor code, improve architecture
    
    Maintenance Balance:
    ✅ Well-maintained: All four types regularly
    ❌ Poorly-maintained: Only corrective (firefighting)
    
    Impact:
    • Well-maintained: Low bugs, low debt, good performance
    • Poorly-maintained: Many bugs, high debt, poor performance
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
    Company A (Well-Maintained):
    • Corrective: Fix bugs weekly
    • Adaptive: Update dependencies monthly
    • Perfective: Performance improvements quarterly
    • Preventive: Refactoring sprints monthly
    • Result: 5 bugs, 20h debt, 90% performance
    
    Company B (Poorly-Maintained):
    • Corrective: Only fix critical bugs
    • Adaptive: Never update (too risky)
    • Perfective: No time for improvements
    • Preventive: No refactoring (not urgent)
    • Result: 47 bugs, 500h debt, 65% performance
    
    After 2 years:
    • Company A: Still maintainable, can add features
    • Company B: Can't add features, must rewrite
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Maintenance is not just bug fixing:
    
    ✅ Corrective: Fix what's broken
    ✅ Adaptive: Keep up with changes
    ✅ Perfective: Improve user experience
    ✅ Preventive: Prevent future problems
    
    Balance all four types:
    • Don't only do corrective (firefighting)
    • Don't ignore adaptive (security risks)
    • Don't skip perfective (user satisfaction)
    • Don't neglect preventive (technical debt)
    
    Remember: Preventive maintenance is like exercise -
    it's easy to skip, but the consequences compound over time!
    """)


if __name__ == "__main__":
    demonstrate_maintainability()


