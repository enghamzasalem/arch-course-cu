#!/usr/bin/env python3
"""
Example 3: Meta-Qualities - Observability, Measurability, and More

This example demonstrates:
- Observability: Can we see what's happening?
- Measurability: Can we quantify quality attributes?
- Repeatability: Do we get consistent results?
- Predictability: Can we forecast quality?
- Auditability: Can we verify quality?
- Accountability: Who is responsible?
- Testability: Can we test quality attributes?

Key Concept: Before measuring any quality attribute, we need meta-qualities
that make measurement possible and meaningful.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import random
import json


# ============================================================================
# BUSINESS SCENARIO: Monitoring and Observability System
# ============================================================================
# A system needs to be observable, measurable, and testable
# to ensure quality attributes are met.
#


class MetaQuality(Enum):
    """Meta-quality attributes"""
    OBSERVABILITY = "observability"
    MEASURABILITY = "measurability"
    REPEATABILITY = "repeatability"
    PREDICTABILITY = "predictability"
    AUDITABILITY = "auditability"
    ACCOUNTABILITY = "accountability"
    TESTABILITY = "testability"


@dataclass
class QualityMetric:
    """A quality metric with meta-qualities"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    observable: bool = True
    measurable: bool = True
    repeatable: bool = True
    predictable: bool = False
    auditable: bool = False
    accountable: str = "unknown"
    testable: bool = False


# ============================================================================
# SYSTEM WITH GOOD META-QUALITIES
# ============================================================================

class ObservableSystem:
    """
    System with good meta-qualities.
    
    Meta-Qualities:
    ✅ Observable: Logs, metrics, traces
    ✅ Measurable: Clear metrics and KPIs
    ✅ Repeatable: Consistent measurements
    ✅ Predictable: Can forecast trends
    ✅ Auditable: Audit logs and history
    ✅ Accountable: Clear ownership
    ✅ Testable: Can test quality attributes
    """
    
    def __init__(self):
        self.metrics: List[QualityMetric] = []
        self.logs: List[Dict] = []
        self.audit_trail: List[Dict] = []
        self.owners: Dict[str, str] = {
            "performance": "backend-team",
            "availability": "ops-team",
            "security": "security-team",
            "cost": "finance-team"
        }
    
    def log_event(self, event: str, level: str = "INFO"):
        """Log an event with timestamp and context"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            "system": "observable-system"
        }
        self.logs.append(log_entry)
        print(f"📝 [{level}] {event}")
    
    def record_metric(self, name: str, value: float, unit: str, 
                     source: str, accountable: Optional[str] = None):
        """Record a quality metric"""
        metric = QualityMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            source=source,
            observable=True,
            measurable=True,
            repeatable=True,
            predictable=True,
            auditable=True,
            accountable=accountable or self.owners.get(name, "system"),
            testable=True
        )
        self.metrics.append(metric)
        self.audit_trail.append({
            "action": "metric_recorded",
            "metric": name,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "recorded_by": accountable or "system"
        })
        print(f"📊 Metric: {name} = {value} {unit}")
    
    def get_observability_report(self) -> Dict:
        """Get observability report"""
        return {
            "logs_count": len(self.logs),
            "metrics_count": len(self.metrics),
            "audit_entries": len(self.audit_trail),
            "observable_metrics": sum(1 for m in self.metrics if m.observable),
            "measurable_metrics": sum(1 for m in self.metrics if m.measurable),
            "testable_metrics": sum(1 for m in self.metrics if m.testable),
            "accountable_metrics": {
                owner: sum(1 for m in self.metrics if m.accountable == owner)
                for owner in set(m.accountable for m in self.metrics)
            }
        }
    
    def predict_metric(self, metric_name: str, days_ahead: int = 7) -> float:
        """Predict a metric value (simple linear prediction)"""
        relevant_metrics = [m for m in self.metrics if m.name == metric_name]
        if len(relevant_metrics) < 2:
            return 0.0
        
        # Simple trend calculation
        recent_values = [m.value for m in relevant_metrics[-10:]]
        if len(recent_values) >= 2:
            trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
            predicted = recent_values[-1] + (trend * days_ahead)
            return max(0, predicted)
        return recent_values[-1]
    
    def audit_metric(self, metric_name: str) -> List[Dict]:
        """Get audit trail for a metric"""
        return [
            entry for entry in self.audit_trail
            if entry.get("metric") == metric_name
        ]
    
    def test_quality_attribute(self, attribute: str, threshold: float) -> bool:
        """Test if a quality attribute meets threshold"""
        relevant_metrics = [m for m in self.metrics if m.name == attribute]
        if not relevant_metrics:
            return False
        
        latest_value = relevant_metrics[-1].value
        meets_threshold = latest_value >= threshold
        
        self.log_event(
            f"Quality test: {attribute} = {latest_value} (threshold: {threshold}) - {'PASS' if meets_threshold else 'FAIL'}",
            "TEST"
        )
        
        return meets_threshold


# ============================================================================
# SYSTEM WITH POOR META-QUALITIES
# ============================================================================

class UnobservableSystem:
    """
    System with poor meta-qualities.
    
    Meta-Qualities:
    ❌ Not Observable: No logs, no metrics
    ❌ Not Measurable: Can't quantify quality
    ❌ Not Repeatable: Inconsistent measurements
    ❌ Not Predictable: Can't forecast
    ❌ Not Auditable: No audit trail
    ❌ Not Accountable: No ownership
    ❌ Not Testable: Can't test quality
    """
    
    def __init__(self):
        self.internal_state = {}  # Hidden state
        self.no_logging = True
        self.no_metrics = True
    
    def do_something(self):
        """Do something - but we can't observe it!"""
        # Internal processing happens, but we can't see it
        self.internal_state["last_action"] = datetime.now()
        # No logging!
        # No metrics!
        # No observability!
        print("🤷 System did something... (but we don't know what)")
    
    def get_quality(self, attribute: str) -> Optional[float]:
        """Try to get quality - but we can't measure it!"""
        print(f"❌ Cannot measure {attribute} - no metrics available")
        return None
    
    def test_quality(self, attribute: str) -> bool:
        """Try to test quality - but we can't test it!"""
        print(f"❌ Cannot test {attribute} - not testable")
        return False


# ============================================================================
# META-QUALITY ANALYZER
# ============================================================================

class MetaQualityAnalyzer:
    """
    Analyzes meta-qualities of a system.
    """
    
    @staticmethod
    def analyze_observability(system) -> Dict:
        """Analyze observability"""
        print("\n" + "=" * 70)
        print("OBSERVABILITY ANALYSIS")
        print("=" * 70)
        
        if isinstance(system, ObservableSystem):
            report = system.get_observability_report()
            print(f"\n✅ Observable System:")
            print(f"   Logs: {report['logs_count']}")
            print(f"   Metrics: {report['metrics_count']}")
            print(f"   Audit Entries: {report['audit_entries']}")
            print(f"   Observable Metrics: {report['observable_metrics']}")
            print(f"   Measurable Metrics: {report['measurable_metrics']}")
            print(f"   Testable Metrics: {report['testable_metrics']}")
            print(f"\n   Accountability:")
            for owner, count in report['accountable_metrics'].items():
                print(f"      {owner}: {count} metrics")
            return report
        else:
            print("\n❌ Unobservable System:")
            print("   No logs available")
            print("   No metrics available")
            print("   Cannot observe system behavior")
            return {"observable": False}
    
    @staticmethod
    def analyze_measurability(system) -> Dict:
        """Analyze measurability"""
        print("\n" + "=" * 70)
        print("MEASURABILITY ANALYSIS")
        print("=" * 70)
        
        if isinstance(system, ObservableSystem):
            print("\n✅ Measurable System:")
            print("   Can quantify quality attributes")
            print("   Has clear metrics and KPIs")
            print("   Can track trends over time")
            
            # Show example measurements
            print("\n   Example Measurements:")
            for metric in system.metrics[-5:]:
                print(f"      {metric.name}: {metric.value} {metric.unit}")
            
            return {"measurable": True}
        else:
            print("\n❌ Not Measurable:")
            print("   Cannot quantify quality attributes")
            print("   No metrics defined")
            print("   Cannot track trends")
            return {"measurable": False}
    
    @staticmethod
    def analyze_testability(system) -> Dict:
        """Analyze testability"""
        print("\n" + "=" * 70)
        print("TESTABILITY ANALYSIS")
        print("=" * 70)
        
        if isinstance(system, ObservableSystem):
            print("\n✅ Testable System:")
            print("   Can test quality attributes")
            print("   Has thresholds defined")
            print("   Can verify quality goals")
            
            # Run some tests
            print("\n   Running Quality Tests:")
            system.test_quality_attribute("performance", threshold=0.8)
            system.test_quality_attribute("availability", threshold=0.99)
            system.test_quality_attribute("security", threshold=0.9)
            
            return {"testable": True}
        else:
            print("\n❌ Not Testable:")
            print("   Cannot test quality attributes")
            print("   No thresholds defined")
            print("   Cannot verify quality")
            return {"testable": False}


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_meta_qualities():
    """
    Demonstrate meta-qualities for quality attributes.
    """
    print("=" * 70)
    print("EXAMPLE 3: Meta-Qualities")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Observability: Can we see what's happening?")
    print("   • Measurability: Can we quantify quality?")
    print("   • Repeatability: Do we get consistent results?")
    print("   • Predictability: Can we forecast quality?")
    print("   • Auditability: Can we verify quality?")
    print("   • Accountability: Who is responsible?")
    print("   • Testability: Can we test quality?")
    
    # Create systems
    observable_system = ObservableSystem()
    unobservable_system = UnobservableSystem()
    
    # Demonstrate observable system
    print("\n" + "=" * 70)
    print("OBSERVABLE SYSTEM")
    print("=" * 70)
    
    observable_system.log_event("System started", "INFO")
    observable_system.record_metric("performance", 0.95, "score", "monitoring", "backend-team")
    observable_system.record_metric("availability", 0.999, "percentage", "monitoring", "ops-team")
    observable_system.record_metric("response_time", 120, "ms", "monitoring", "backend-team")
    observable_system.record_metric("error_rate", 0.001, "percentage", "monitoring", "backend-team")
    observable_system.record_metric("cost", 500, "dollars/month", "billing", "finance-team")
    
    # Analyze meta-qualities
    MetaQualityAnalyzer.analyze_observability(observable_system)
    MetaQualityAnalyzer.analyze_measurability(observable_system)
    MetaQualityAnalyzer.analyze_testability(observable_system)
    
    # Demonstrate prediction
    print("\n" + "=" * 70)
    print("PREDICTABILITY")
    print("=" * 70)
    predicted_performance = observable_system.predict_metric("performance", days_ahead=7)
    print(f"\n📈 Predicted performance in 7 days: {predicted_performance:.2f}")
    
    # Demonstrate auditability
    print("\n" + "=" * 70)
    print("AUDITABILITY")
    print("=" * 70)
    audit_trail = observable_system.audit_metric("performance")
    print(f"\n📋 Audit trail for 'performance': {len(audit_trail)} entries")
    for entry in audit_trail[-3:]:
        print(f"   {entry['timestamp']}: {entry['action']} = {entry['value']}")
    
    # Demonstrate unobservable system
    print("\n" + "=" * 70)
    print("UNOBSERVABLE SYSTEM")
    print("=" * 70)
    
    unobservable_system.do_something()
    unobservable_system.get_quality("performance")
    unobservable_system.test_quality("availability")
    
    MetaQualityAnalyzer.analyze_observability(unobservable_system)
    MetaQualityAnalyzer.analyze_measurability(unobservable_system)
    MetaQualityAnalyzer.analyze_testability(unobservable_system)
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Meta-Qualities Checklist:
    
    ✅ Observability:
       - Can you see what the system is doing?
       - Do you have logs, metrics, traces?
       - Can you debug issues?
    
    ✅ Measurability:
       - Can you quantify quality attributes?
       - Do you have clear metrics?
       - Can you track trends?
    
    ✅ Repeatability:
       - Do measurements give consistent results?
       - Can you reproduce measurements?
       - Is there measurement jitter?
    
    ✅ Predictability:
       - Can you forecast quality trends?
       - Can you predict when thresholds will be breached?
       - Can you plan based on predictions?
    
    ✅ Auditability:
       - Can you verify quality claims?
       - Do you have audit logs?
       - Can you trace quality changes?
    
    ✅ Accountability:
       - Who is responsible for each quality attribute?
       - Is ownership clear?
       - Can you escalate issues?
    
    ✅ Testability:
       - Can you test quality attributes?
       - Do you have test thresholds?
       - Can you verify quality goals?
    
    Without meta-qualities:
    ❌ You can't measure quality
    ❌ You can't improve quality
    ❌ You can't verify quality
    ❌ You can't be accountable for quality
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
    Company A (Good Meta-Qualities):
    • Observability: Comprehensive logging and monitoring
    • Measurability: Clear KPIs for all quality attributes
    • Testability: Automated quality tests in CI/CD
    • Accountability: Each team owns specific quality attributes
    • Result: Can measure, improve, and verify quality
    
    Company B (Poor Meta-Qualities):
    • Observability: No logs, no metrics
    • Measurability: Can't quantify quality
    • Testability: No quality tests
    • Accountability: Nobody knows who's responsible
    • Result: Flying blind, can't improve quality
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Before measuring quality attributes, ensure meta-qualities:
    
    1. Make it Observable:
       - Add logging, metrics, traces
       - Use monitoring tools
    
    2. Make it Measurable:
       - Define clear metrics
       - Set up measurement infrastructure
    
    3. Make it Testable:
       - Define test thresholds
       - Automate quality tests
    
    4. Make it Accountable:
       - Assign ownership
       - Set up escalation paths
    
    Remember: You can't improve what you can't measure!
    And you can't measure without meta-qualities!
    """)


if __name__ == "__main__":
    demonstrate_meta_qualities()

