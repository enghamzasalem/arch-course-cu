#!/usr/bin/env python3
"""
Example 1: Internal vs. External Quality Attributes

This example demonstrates:
- Internal quality: Developer experience, code maintainability
- External quality: User experience, system behavior
- How internal quality affects external quality over time
- Real-world business scenario: E-commerce Platform

Key Concept: Internal quality is invisible to users but critical for
long-term success. External quality is what users experience directly.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time


# ============================================================================
# BUSINESS SCENARIO: E-commerce Platform
# ============================================================================
# Internal quality affects developers: Can they add features quickly?
# External quality affects users: Is the site fast and reliable?
# Over time, poor internal quality degrades external quality.
#


class CodeQuality(Enum):
    """Internal code quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    TERRIBLE = "terrible"


class UserExperience(Enum):
    """External user experience levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    TERRIBLE = "terrible"


@dataclass
class InternalQualityMetrics:
    """Internal quality metrics (developer-facing)"""
    code_complexity: float  # Cyclomatic complexity
    test_coverage: float  # Percentage
    documentation_quality: float  # 0-1 score
    code_review_time: float  # Hours
    refactoring_frequency: float  # Times per month
    technical_debt: float  # Hours of debt
    developer_satisfaction: float  # 0-1 score


@dataclass
class ExternalQualityMetrics:
    """External quality metrics (user-facing)"""
    page_load_time: float  # Seconds
    error_rate: float  # Percentage
    availability: float  # Percentage
    feature_completeness: float  # 0-1 score
    user_satisfaction: float  # 0-1 score
    response_time: float  # Seconds


# ============================================================================
# SYSTEM WITH GOOD INTERNAL QUALITY
# ============================================================================

class WellArchitectedECommercePlatform:
    """
    E-commerce platform with good internal quality.
    
    Internal Quality (Developer Experience):
    ✅ Clean, modular code
    ✅ High test coverage
    ✅ Good documentation
    ✅ Fast development cycles
    
    External Quality (User Experience):
    ✅ Fast page loads
    ✅ Low error rates
    ✅ High availability
    ✅ Regular feature updates
    """
    
    def __init__(self):
        self.internal_quality = InternalQualityMetrics(
            code_complexity=5.2,  # Low complexity
            test_coverage=0.85,  # 85% coverage
            documentation_quality=0.9,
            code_review_time=2.0,  # 2 hours per PR
            refactoring_frequency=4.0,  # Regular refactoring
            technical_debt=10.0,  # Low debt
            developer_satisfaction=0.85
        )
        self.external_quality = ExternalQualityMetrics(
            page_load_time=0.8,  # Fast
            error_rate=0.01,  # 0.01% errors
            availability=0.999,  # 99.9% uptime
            feature_completeness=0.95,
            user_satisfaction=0.88,
            response_time=0.5
        )
        self.features_deployed = 0
        self.months_in_production = 0
    
    def add_feature(self, feature_name: str) -> bool:
        """Add a new feature - fast because of good internal quality"""
        print(f"  ✅ Adding feature: {feature_name}")
        
        # Good internal quality = fast development
        development_time = 2.0  # 2 days (fast!)
        test_time = 0.5  # Well-tested code
        review_time = self.internal_quality.code_review_time
        
        total_time = development_time + test_time + review_time
        print(f"     Development: {development_time} days")
        print(f"     Testing: {test_time} days")
        print(f"     Review: {review_time} hours")
        print(f"     Total: {total_time:.1f} days")
        
        self.features_deployed += 1
        return True
    
    def get_quality_report(self) -> Dict:
        """Get comprehensive quality report"""
        return {
            "internal": {
                "code_complexity": self.internal_quality.code_complexity,
                "test_coverage": f"{self.internal_quality.test_coverage * 100:.1f}%",
                "developer_satisfaction": f"{self.internal_quality.developer_satisfaction * 100:.0f}%",
                "technical_debt": f"{self.internal_quality.technical_debt} hours"
            },
            "external": {
                "page_load_time": f"{self.external_quality.page_load_time:.2f}s",
                "error_rate": f"{self.external_quality.error_rate * 100:.2f}%",
                "availability": f"{self.external_quality.availability * 100:.2f}%",
                "user_satisfaction": f"{self.external_quality.user_satisfaction * 100:.0f}%"
            }
        }


# ============================================================================
# SYSTEM WITH POOR INTERNAL QUALITY
# ============================================================================

class PoorlyArchitectedECommercePlatform:
    """
    E-commerce platform with poor internal quality.
    
    Internal Quality (Developer Experience):
    ❌ Spaghetti code
    ❌ Low test coverage
    ❌ Poor documentation
    ❌ Slow development cycles
    
    External Quality (User Experience):
    ⚠️ Initially OK, but degrades over time
    ❌ Bugs accumulate
    ❌ Features take longer
    ❌ More downtime
    """
    
    def __init__(self):
        self.internal_quality = InternalQualityMetrics(
            code_complexity=25.8,  # High complexity
            test_coverage=0.15,  # Only 15% coverage
            documentation_quality=0.2,
            code_review_time=8.0,  # 8 hours per PR (complex code)
            refactoring_frequency=0.1,  # Rarely refactored
            technical_debt=500.0,  # High debt
            developer_satisfaction=0.35
        )
        self.external_quality = ExternalQualityMetrics(
            page_load_time=1.2,  # Slower
            error_rate=0.05,  # 0.05% errors (5x worse)
            availability=0.985,  # 98.5% uptime (worse)
            feature_completeness=0.70,  # Missing features
            user_satisfaction=0.65,  # Lower satisfaction
            response_time=1.2
        )
        self.features_deployed = 0
        self.months_in_production = 0
        self.bugs_introduced = 0
    
    def add_feature(self, feature_name: str) -> bool:
        """Add a new feature - slow because of poor internal quality"""
        print(f"  ⚠️  Adding feature: {feature_name}")
        
        # Poor internal quality = slow development
        development_time = 8.0  # 8 days (4x slower!)
        test_time = 2.0  # More bugs to fix
        review_time = self.internal_quality.code_review_time
        
        # High complexity = more bugs
        bugs = 3  # Average bugs per feature
        bug_fix_time = bugs * 1.5  # 1.5 days per bug
        
        total_time = development_time + test_time + review_time + bug_fix_time
        print(f"     Development: {development_time} days")
        print(f"     Testing: {test_time} days")
        print(f"     Review: {review_time} hours")
        print(f"     Bug fixes: {bug_fix_time} days ({bugs} bugs)")
        print(f"     Total: {total_time:.1f} days")
        
        self.features_deployed += 1
        self.bugs_introduced += bugs
        
        # External quality degrades over time
        self.external_quality.error_rate += 0.001
        self.external_quality.user_satisfaction -= 0.01
        
        return True
    
    def get_quality_report(self) -> Dict:
        """Get comprehensive quality report"""
        return {
            "internal": {
                "code_complexity": self.internal_quality.code_complexity,
                "test_coverage": f"{self.internal_quality.test_coverage * 100:.1f}%",
                "developer_satisfaction": f"{self.internal_quality.developer_satisfaction * 100:.0f}%",
                "technical_debt": f"{self.internal_quality.technical_debt} hours"
            },
            "external": {
                "page_load_time": f"{self.external_quality.page_load_time:.2f}s",
                "error_rate": f"{self.external_quality.error_rate * 100:.2f}%",
                "availability": f"{self.external_quality.availability * 100:.2f}%",
                "user_satisfaction": f"{self.external_quality.user_satisfaction * 100:.0f}%"
            }
        }


# ============================================================================
# QUALITY EVOLUTION OVER TIME
# ============================================================================

class QualityEvolutionAnalyzer:
    """
    Analyzes how internal quality affects external quality over time.
    """
    
    @staticmethod
    def simulate_6_months(platform, platform_name: str):
        """Simulate 6 months of development"""
        print(f"\n{'=' * 70}")
        print(f"SIMULATING 6 MONTHS: {platform_name}")
        print(f"{'=' * 70}")
        
        features_to_add = [
            "User Authentication",
            "Product Search",
            "Shopping Cart",
            "Payment Processing",
            "Order Tracking",
            "Product Reviews",
            "Recommendation Engine",
            "Wishlist",
            "Coupon System",
            "Inventory Management"
        ]
        
        print(f"\n📅 Month 1-6: Adding {len(features_to_add)} features")
        print("-" * 70)
        
        total_days = 0
        for i, feature in enumerate(features_to_add, 1):
            print(f"\nMonth {(i-1)//2 + 1}, Feature {i}:")
            success = platform.add_feature(feature)
            if success:
                # Estimate days based on platform type
                if isinstance(platform, WellArchitectedECommercePlatform):
                    total_days += 2.5
                else:
                    total_days += 12.0
        
        print(f"\n{'=' * 70}")
        print("QUALITY METRICS AFTER 6 MONTHS")
        print(f"{'=' * 70}")
        report = platform.get_quality_report()
        
        print("\n📊 Internal Quality (Developer Experience):")
        for key, value in report["internal"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\n👥 External Quality (User Experience):")
        for key, value in report["external"].items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        if isinstance(platform, PoorlyArchitectedECommercePlatform):
            print(f"\n🐛 Bugs Introduced: {platform.bugs_introduced}")
            print(f"⏱️  Total Development Time: {total_days:.0f} days")
        else:
            print(f"⏱️  Total Development Time: {total_days:.0f} days")
        
        return report


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_internal_vs_external_quality():
    """
    Demonstrate the relationship between internal and external quality.
    """
    print("=" * 70)
    print("EXAMPLE 1: Internal vs. External Quality Attributes")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Internal Quality: Developer experience, code maintainability")
    print("   • External Quality: User experience, system behavior")
    print("   • Internal quality affects external quality over time")
    print("   • Poor internal quality → slower development → worse external quality")
    
    # Create platforms
    good_platform = WellArchitectedECommercePlatform()
    bad_platform = PoorlyArchitectedECommercePlatform()
    
    # Simulate 6 months
    print("\n" + "=" * 70)
    print("COMPARISON: Good vs. Poor Internal Quality")
    print("=" * 70)
    
    good_report = QualityEvolutionAnalyzer.simulate_6_months(
        good_platform, "Well-Architected Platform"
    )
    
    bad_report = QualityEvolutionAnalyzer.simulate_6_months(
        bad_platform, "Poorly-Architected Platform"
    )
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Internal Quality Impact:
    
    1. Development Speed:
       ✅ Good internal quality: 2.5 days per feature
       ❌ Poor internal quality: 12 days per feature (5x slower!)
    
    2. Bug Introduction:
       ✅ Good internal quality: ~0 bugs per feature
       ❌ Poor internal quality: ~3 bugs per feature
    
    3. External Quality Over Time:
       ✅ Good internal quality: Maintains high user satisfaction
       ❌ Poor internal quality: User satisfaction degrades
    
    4. Technical Debt:
       ✅ Good internal quality: 10 hours of debt
       ❌ Poor internal quality: 500 hours of debt (50x more!)
    
    5. Developer Satisfaction:
       ✅ Good internal quality: 85% satisfied
       ❌ Poor internal quality: 35% satisfied (burnout risk!)
    
    Business Impact:
    • Feature delivery: 5x faster with good internal quality
    • Bug fixes: More time fixing bugs = less time on features
    • Team retention: Happy developers stay longer
    • User satisfaction: Better code = better user experience
    • Cost: Technical debt compounds over time
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
    Company A (Good Internal Quality):
    • 10 features in 6 months
    • 2 bugs total
    • 99.9% uptime
    • 88% user satisfaction
    • Team of 5 developers
    
    Company B (Poor Internal Quality):
    • 10 features in 6 months (but took 5x longer)
    • 30 bugs total
    • 98.5% uptime
    • 65% user satisfaction
    • Team of 5 developers (but 2 quit due to burnout)
    
    Result: Company A ships faster, has happier users, and keeps developers.
    Company B struggles with bugs, loses users, and has high turnover.
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Internal quality is invisible to users but critical for success:
    
    ✅ Invest in internal quality early
    ✅ Maintain code quality continuously
    ✅ Refactor regularly to reduce technical debt
    ✅ Write tests to catch bugs early
    ✅ Document code for future developers
    
    External quality is what users see, but it depends on internal quality:
    ✅ Fast development = more features = happier users
    ✅ Fewer bugs = better reliability = higher satisfaction
    ✅ Happy developers = better code = better products
    
    Remember: You can't have good external quality without good internal quality!
    """)


if __name__ == "__main__":
    demonstrate_internal_vs_external_quality()


