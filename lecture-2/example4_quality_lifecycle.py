#!/usr/bin/env python3
"""
Example 4: Quality Attributes Across Software Lifecycle

This example demonstrates:
- Quality in Design: Architecture decisions
- Quality in Operation: Normal runtime behavior
- Quality in Failure: Error handling and recovery
- Quality in Attack: Security and resilience
- Quality in Change: Adaptability and evolution
- Quality in Long-term: Sustainability

Key Concept: Quality attributes manifest differently at different stages
of the software lifecycle. A system must handle all of them.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import time
import random


# ============================================================================
# BUSINESS SCENARIO: Banking System
# ============================================================================
# A banking system must maintain quality across all lifecycle stages:
# - Design: Architecture decisions affect future quality
# - Operation: Must work reliably 24/7
# - Failure: Must handle errors gracefully
# - Attack: Must resist security threats
# - Change: Must adapt to new requirements
# - Long-term: Must remain viable for years
#


class LifecycleStage(Enum):
    """Stages of software lifecycle"""
    DESIGN = "design"
    OPERATION = "operation"
    FAILURE = "failure"
    ATTACK = "attack"
    CHANGE = "change"
    LONG_TERM = "long_term"


@dataclass
class QualityAtStage:
    """Quality attributes at a specific lifecycle stage"""
    stage: LifecycleStage
    performance: float  # 0-1
    reliability: float  # 0-1
    security: float  # 0-1
    maintainability: float  # 0-1
    availability: float  # 0-1


# ============================================================================
# BANKING SYSTEM WITH QUALITY ACROSS LIFECYCLE
# ============================================================================

class QualityBankingSystem:
    """
    Banking system designed for quality across all lifecycle stages.
    
    Design Stage:
    ✅ Modular architecture
    ✅ Security by design
    ✅ Scalable design
    ✅ Maintainable structure
    
    Operation Stage:
    ✅ High availability
    ✅ Fast response times
    ✅ Reliable transactions
    ✅ Real-time monitoring
    
    Failure Stage:
    ✅ Graceful error handling
    ✅ Automatic recovery
    ✅ Data consistency
    ✅ Transaction rollback
    
    Attack Stage:
    ✅ Security controls
    ✅ Intrusion detection
    ✅ Rate limiting
    ✅ Encryption
    
    Change Stage:
    ✅ Modular design
    ✅ API versioning
    ✅ Feature flags
    ✅ Backward compatibility
    
    Long-term Stage:
    ✅ Technical sustainability
    ✅ Economic viability
    ✅ Growth planning
    """
    
    def __init__(self):
        self.quality_at_stages = {
            LifecycleStage.DESIGN: QualityAtStage(
                stage=LifecycleStage.DESIGN,
                performance=0.95,
                reliability=0.98,
                security=0.99,
                maintainability=0.92,
                availability=0.0  # Not deployed yet
            ),
            LifecycleStage.OPERATION: QualityAtStage(
                stage=LifecycleStage.OPERATION,
                performance=0.94,
                reliability=0.997,
                security=0.98,
                maintainability=0.90,
                availability=0.9995  # 99.95% uptime
            ),
            LifecycleStage.FAILURE: QualityAtStage(
                stage=LifecycleStage.FAILURE,
                performance=0.85,  # Degraded during failure
                reliability=0.95,  # Still reliable
                security=0.98,
                maintainability=0.90,
                availability=0.99  # Degraded but still available
            ),
            LifecycleStage.ATTACK: QualityAtStage(
                stage=LifecycleStage.ATTACK,
                performance=0.80,  # Degraded under attack
                reliability=0.90,
                security=0.95,  # Security holds
                maintainability=0.90,
                availability=0.98  # Degraded but operational
            ),
            LifecycleStage.CHANGE: QualityAtStage(
                stage=LifecycleStage.CHANGE,
                performance=0.92,
                reliability=0.95,
                security=0.98,
                maintainability=0.88,  # Slightly degraded during change
                availability=0.995  # Minor downtime for updates
            ),
            LifecycleStage.LONG_TERM: QualityAtStage(
                stage=LifecycleStage.LONG_TERM,
                performance=0.90,  # May degrade over time
                reliability=0.95,
                security=0.97,  # Must keep up with threats
                maintainability=0.85,  # May accumulate technical debt
                availability=0.99  # Maintained over years
            )
        }
        self.transactions_processed = 0
        self.failures_handled = 0
        self.attacks_blocked = 0
        self.changes_applied = 0
        self.years_in_production = 0
    
    def design_phase(self):
        """Design phase - architecture decisions"""
        print("\n" + "=" * 70)
        print("DESIGN STAGE: Architecture Decisions")
        print("=" * 70)
        print("""
        ✅ Modular architecture: Easy to maintain
        ✅ Security by design: Built-in security controls
        ✅ Scalable design: Can handle growth
        ✅ Monitoring: Observability from day one
        ✅ Testability: Architecture supports testing
        
        Quality at Design:
        • Performance: 95% (optimized architecture)
        • Reliability: 98% (redundancy designed in)
        • Security: 99% (security-first design)
        • Maintainability: 92% (clean architecture)
        """)
        return self.quality_at_stages[LifecycleStage.DESIGN]
    
    def operate(self, transaction: str) -> bool:
        """Operation phase - normal runtime"""
        print(f"\n💳 Processing transaction: {transaction}")
        
        # Simulate processing
        processing_time = 0.05 + random.uniform(0, 0.02)
        time.sleep(processing_time)
        
        # High reliability
        success = random.random() > 0.003  # 99.7% success rate
        
        if success:
            self.transactions_processed += 1
            print(f"   ✅ Transaction successful ({processing_time*1000:.0f}ms)")
        else:
            print(f"   ❌ Transaction failed (handled gracefully)")
            self.failures_handled += 1
        
        return success
    
    def handle_failure(self, failure_type: str):
        """Failure phase - error handling"""
        print("\n" + "=" * 70)
        print(f"FAILURE STAGE: Handling {failure_type}")
        print("=" * 70)
        
        print("""
        ✅ Graceful degradation: System continues operating
        ✅ Automatic recovery: Self-healing mechanisms
        ✅ Data consistency: Transactions rolled back safely
        ✅ Error logging: Issues tracked and monitored
        ✅ User notification: Users informed of issues
        
        Quality during Failure:
        • Performance: 85% (degraded but functional)
        • Reliability: 95% (still reliable)
        • Security: 98% (security maintained)
        • Availability: 99% (degraded but available)
        """)
        
        self.failures_handled += 1
        return self.quality_at_stages[LifecycleStage.FAILURE]
    
    def handle_attack(self, attack_type: str):
        """Attack phase - security response"""
        print("\n" + "=" * 70)
        print(f"ATTACK STAGE: Defending against {attack_type}")
        print("=" * 70)
        
        print("""
        ✅ Intrusion detection: Attacks detected
        ✅ Rate limiting: DDoS mitigated
        ✅ Authentication: Unauthorized access blocked
        ✅ Encryption: Data protected
        ✅ Audit logging: Attacks logged for analysis
        
        Quality during Attack:
        • Performance: 80% (degraded under attack)
        • Reliability: 90% (still operational)
        • Security: 95% (security controls hold)
        • Availability: 98% (degraded but available)
        """)
        
        self.attacks_blocked += 1
        return self.quality_at_stages[LifecycleStage.ATTACK]
    
    def apply_change(self, change_description: str):
        """Change phase - system evolution"""
        print("\n" + "=" * 70)
        print(f"CHANGE STAGE: Applying {change_description}")
        print("=" * 70)
        
        print("""
        ✅ Modular design: Changes isolated to modules
        ✅ API versioning: Backward compatibility maintained
        ✅ Feature flags: Gradual rollout
        ✅ Testing: Changes tested before deployment
        ✅ Rollback: Can revert if issues occur
        
        Quality during Change:
        • Performance: 92% (slight impact)
        • Reliability: 95% (maintained)
        • Security: 98% (maintained)
        • Maintainability: 88% (temporarily lower)
        • Availability: 99.5% (minor downtime)
        """)
        
        self.changes_applied += 1
        return self.quality_at_stages[LifecycleStage.CHANGE]
    
    def long_term_sustainability(self, years: int):
        """Long-term phase - sustainability"""
        print("\n" + "=" * 70)
        print(f"LONG-TERM STAGE: {years} Years in Production")
        print("=" * 70)
        
        print(f"""
        ✅ Technical sustainability: Dependencies managed
        ✅ Economic sustainability: Cost-effective operations
        ✅ Growth sustainability: Scalable architecture
        ✅ Maintenance: Regular updates and improvements
        
        Quality over Long-term:
        • Performance: 90% (may degrade, but maintained)
        • Reliability: 95% (maintained over years)
        • Security: 97% (kept up-to-date)
        • Maintainability: 85% (some technical debt)
        • Availability: 99% (maintained)
        
        Statistics:
        • Transactions processed: {self.transactions_processed:,}
        • Failures handled: {self.failures_handled}
        • Attacks blocked: {self.attacks_blocked}
        • Changes applied: {self.changes_applied}
        """)
        
        self.years_in_production = years
        return self.quality_at_stages[LifecycleStage.LONG_TERM]
    
    def get_quality_report(self) -> Dict:
        """Get quality report across all stages"""
        return {
            stage.value: {
                "performance": f"{quality.performance * 100:.0f}%",
                "reliability": f"{quality.reliability * 100:.0f}%",
                "security": f"{quality.security * 100:.0f}%",
                "maintainability": f"{quality.maintainability * 100:.0f}%",
                "availability": f"{quality.availability * 100:.2f}%" if quality.availability > 0 else "N/A"
            }
            for stage, quality in self.quality_at_stages.items()
        }


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_quality_lifecycle():
    """
    Demonstrate quality attributes across software lifecycle.
    """
    print("=" * 70)
    print("EXAMPLE 4: Quality Attributes Across Software Lifecycle")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Design: Architecture decisions affect future quality")
    print("   • Operation: System behavior under normal conditions")
    print("   • Failure: How system handles errors and failures")
    print("   • Attack: Security and resilience to attacks")
    print("   • Change: How system adapts to new requirements")
    print("   • Long-term: Sustainability and evolution over years")
    
    # Create banking system
    banking_system = QualityBankingSystem()
    
    # Simulate lifecycle
    print("\n" + "=" * 70)
    print("SIMULATING SOFTWARE LIFECYCLE")
    print("=" * 70)
    
    # 1. Design phase
    banking_system.design_phase()
    
    # 2. Operation phase
    print("\n" + "=" * 70)
    print("OPERATION STAGE: Normal Runtime")
    print("=" * 70)
    print("\nProcessing transactions...")
    for i in range(10):
        banking_system.operate(f"Transaction-{i+1}")
    
    # 3. Failure phase
    banking_system.handle_failure("Database Connection Loss")
    
    # 4. Attack phase
    banking_system.handle_attack("DDoS Attack")
    
    # 5. Change phase
    banking_system.apply_change("New Payment Method Integration")
    
    # 6. Long-term phase
    banking_system.long_term_sustainability(years=5)
    
    # Quality report
    print("\n" + "=" * 70)
    print("QUALITY REPORT ACROSS LIFECYCLE")
    print("=" * 70)
    report = banking_system.get_quality_report()
    for stage, metrics in report.items():
        print(f"\n{stage.upper().replace('_', ' ')}:")
        for metric, value in metrics.items():
            print(f"   {metric.title()}: {value}")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Quality Attributes at Each Stage:
    
    1. Design Stage:
       • Set the foundation for all future quality
       • Architecture decisions are hard to change later
       • Invest time in good design
    
    2. Operation Stage:
       • Normal runtime behavior
       • Must meet SLAs and performance targets
       • Continuous monitoring required
    
    3. Failure Stage:
       • System must degrade gracefully
       • Errors must be handled safely
       • Recovery mechanisms must work
    
    4. Attack Stage:
       • Security must hold under attack
       • System must remain operational
       • Attacks must be detected and logged
    
    5. Change Stage:
       • System must adapt to new requirements
       • Changes must not break existing functionality
       • Backward compatibility important
    
    6. Long-term Stage:
       • System must remain viable for years
       • Technical debt must be managed
       • Dependencies must be maintained
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
    Banking System Requirements:
    
    Design:
    • Must support 1M+ transactions/day
    • Must be secure by design
    • Must be maintainable for 10+ years
    
    Operation:
    • 99.95% uptime requirement
    • <100ms response time
    • Zero data loss
    
    Failure:
    • Automatic failover to backup systems
    • Transaction rollback on errors
    • User notification of issues
    
    Attack:
    • Multi-factor authentication
    • Rate limiting and DDoS protection
    • Encryption at rest and in transit
    
    Change:
    • API versioning for backward compatibility
    • Feature flags for gradual rollout
    • Comprehensive testing before deployment
    
    Long-term:
    • Regular security updates
    • Dependency management
    • Technical debt reduction
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Quality attributes must be considered at every stage:
    
    ✅ Design: Plan for quality from the start
    ✅ Operation: Monitor and maintain quality
    ✅ Failure: Handle errors gracefully
    ✅ Attack: Defend against threats
    ✅ Change: Evolve without breaking
    ✅ Long-term: Sustain quality over years
    
    Remember: Quality is not just about operation!
    It must be designed in, maintained during operation,
    preserved during failures and attacks, and sustained long-term.
    """)


if __name__ == "__main__":
    demonstrate_quality_lifecycle()


