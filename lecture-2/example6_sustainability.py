#!/usr/bin/env python3
"""
Example 6: Sustainability - Technical, Economic, and Growth

This example demonstrates:
- Technical Sustainability: Avoiding obsolescence
- Economic Sustainability: Business viability and monetization
- Growth Sustainability: Sustainable scaling

Key Concept: A system must be sustainable in multiple dimensions
to survive long-term. Technical excellence alone is not enough.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time


# ============================================================================
# BUSINESS SCENARIO: Startup to Scale-up Journey
# ============================================================================
# A startup must balance:
# - Technical: Keep technology current
# - Economic: Make money and control costs
# - Growth: Scale without breaking
#


class SustainabilityDimension(Enum):
    """Dimensions of sustainability"""
    TECHNICAL = "technical"
    ECONOMIC = "economic"
    GROWTH = "growth"


@dataclass
class TechnicalSustainability:
    """Technical sustainability metrics"""
    dependency_health: float  # 0-1
    platform_compatibility: float  # 0-1
    security_updates: float  # 0-1
    obsolescence_risk: float  # 0-1, lower is better
    technical_debt: float  # hours


@dataclass
class EconomicSustainability:
    """Economic sustainability metrics"""
    revenue: float  # dollars/month
    costs: float  # dollars/month
    profit_margin: float  # 0-1
    burn_rate: float  # dollars/month
    runway_months: float  # months until out of money
    monetization_strategy: str


@dataclass
class GrowthSustainability:
    """Growth sustainability metrics"""
    user_count: int
    growth_rate: float  # percentage/month
    cost_per_user: float  # dollars
    infrastructure_cost: float  # dollars/month
    can_scale: bool


# ============================================================================
# SUSTAINABLE STARTUP
# ============================================================================

class SustainableStartup:
    """
    Startup with sustainable approach across all dimensions.
    
    Technical Sustainability:
    ✅ Regular dependency updates
    ✅ Modern technology stack
    ✅ Security patches applied
    ✅ Low technical debt
    
    Economic Sustainability:
    ✅ Clear monetization strategy
    ✅ Cost-effective infrastructure
    ✅ Positive unit economics
    ✅ Sufficient runway
    
    Growth Sustainability:
    ✅ Scalable architecture
    ✅ Cost per user decreases with scale
    ✅ Can handle growth
    """
    
    def __init__(self):
        self.technical = TechnicalSustainability(
            dependency_health=0.95,
            platform_compatibility=0.98,
            security_updates=0.99,
            obsolescence_risk=0.05,
            technical_debt=15.0
        )
        self.economic = EconomicSustainability(
            revenue=5000.0,
            costs=3000.0,
            profit_margin=0.40,
            burn_rate=0.0,  # Profitable!
            runway_months=float('inf'),  # Infinite (profitable)
            monetization_strategy="Freemium with premium features"
        )
        self.growth = GrowthSustainability(
            user_count=1000,
            growth_rate=20.0,  # 20% per month
            cost_per_user=3.0,
            infrastructure_cost=3000.0,
            can_scale=True
        )
        self.months_operating = 0
    
    def maintain_technical_sustainability(self):
        """Maintain technical sustainability"""
        print("\n" + "=" * 70)
        print("TECHNICAL SUSTAINABILITY")
        print("=" * 70)
        print("""
        ✅ Regular dependency updates: Monthly
        ✅ Security patches: Applied immediately
        ✅ Platform compatibility: Tested regularly
        ✅ Technical debt: Managed actively
        
        Metrics:
        • Dependency Health: 95%
        • Platform Compatibility: 98%
        • Security Updates: 99%
        • Obsolescence Risk: 5% (low)
        • Technical Debt: 15 hours
        """)
        
        # Simulate maintenance
        self.technical.technical_debt = max(0, self.technical.technical_debt - 2.0)
        self.technical.dependency_health = min(1.0, self.technical.dependency_health + 0.01)
    
    def maintain_economic_sustainability(self):
        """Maintain economic sustainability"""
        print("\n" + "=" * 70)
        print("ECONOMIC SUSTAINABILITY")
        print("=" * 70)
        print(f"""
        ✅ Monetization: {self.economic.monetization_strategy}
        ✅ Revenue: ${self.economic.revenue:,.0f}/month
        ✅ Costs: ${self.economic.costs:,.0f}/month
        ✅ Profit: ${self.economic.revenue - self.economic.costs:,.0f}/month
        ✅ Profit Margin: {self.economic.profit_margin * 100:.0f}%
        ✅ Runway: {'Infinite (profitable!)' if self.economic.runway_months == float('inf') else f'{self.economic.runway_months:.0f} months'}
        
        Strategy:
        • Free tier: Attract users
        • Premium tier: Generate revenue
        • Cost optimization: Use efficient infrastructure
        """)
        
        # Simulate growth
        self.economic.revenue += 500  # Growing revenue
        self.economic.costs += 200  # Costs grow slower
    
    def maintain_growth_sustainability(self):
        """Maintain growth sustainability"""
        print("\n" + "=" * 70)
        print("GROWTH SUSTAINABILITY")
        print("=" * 70)
        print(f"""
        ✅ Users: {self.growth.user_count:,}
        ✅ Growth Rate: {self.growth.growth_rate:.0f}%/month
        ✅ Cost per User: ${self.growth.cost_per_user:.2f}
        ✅ Infrastructure Cost: ${self.growth.infrastructure_cost:,.0f}/month
        ✅ Can Scale: {'Yes' if self.growth.can_scale else 'No'}
        
        Scaling Strategy:
        • Architecture supports horizontal scaling
        • Cost per user decreases with scale
        • Infrastructure scales automatically
        """)
        
        # Simulate growth
        new_users = int(self.growth.user_count * (self.growth.growth_rate / 100))
        self.growth.user_count += new_users
        
        # Cost per user decreases with scale (economies of scale)
        if self.growth.user_count > 0:
            self.growth.cost_per_user = max(1.0, self.growth.infrastructure_cost / self.growth.user_count)
    
    def simulate_month(self):
        """Simulate one month of operation"""
        self.months_operating += 1
        print(f"\n{'=' * 70}")
        print(f"MONTH {self.months_operating}")
        print(f"{'=' * 70}")
        
        self.maintain_technical_sustainability()
        self.maintain_economic_sustainability()
        self.maintain_growth_sustainability()
    
    def get_sustainability_report(self) -> Dict:
        """Get sustainability report"""
        return {
            "technical": {
                "dependency_health": f"{self.technical.dependency_health * 100:.0f}%",
                "platform_compatibility": f"{self.technical.platform_compatibility * 100:.0f}%",
                "security_updates": f"{self.technical.security_updates * 100:.0f}%",
                "obsolescence_risk": f"{self.technical.obsolescence_risk * 100:.0f}%",
                "technical_debt": f"{self.technical.technical_debt:.0f} hours"
            },
            "economic": {
                "revenue": f"${self.economic.revenue:,.0f}/month",
                "costs": f"${self.economic.costs:,.0f}/month",
                "profit": f"${self.economic.revenue - self.economic.costs:,.0f}/month",
                "profit_margin": f"{self.economic.profit_margin * 100:.0f}%",
                "runway": "Infinite (profitable)" if self.economic.runway_months == float('inf') else f"{self.economic.runway_months:.0f} months"
            },
            "growth": {
                "users": f"{self.growth.user_count:,}",
                "growth_rate": f"{self.growth.growth_rate:.0f}%/month",
                "cost_per_user": f"${self.growth.cost_per_user:.2f}",
                "can_scale": "Yes" if self.growth.can_scale else "No"
            }
        }


# ============================================================================
# UNSUSTAINABLE STARTUP
# ============================================================================

class UnsustainableStartup:
    """
    Startup with unsustainable approach.
    
    Technical Sustainability:
    ❌ Outdated dependencies
    ❌ No security updates
    ❌ High obsolescence risk
    ❌ High technical debt
    
    Economic Sustainability:
    ❌ No monetization strategy
    ❌ High burn rate
    ❌ Limited runway
    ❌ Negative unit economics
    
    Growth Sustainability:
    ❌ Can't scale cost-effectively
    ❌ Cost per user increases
    ❌ "Death by success"
    """
    
    def __init__(self):
        self.technical = TechnicalSustainability(
            dependency_health=0.35,
            platform_compatibility=0.60,
            security_updates=0.20,
            obsolescence_risk=0.75,  # High risk!
            technical_debt=500.0  # High debt!
        )
        self.economic = EconomicSustainability(
            revenue=0.0,  # No revenue!
            costs=5000.0,  # High costs!
            profit_margin=-1.0,  # Losing money!
            burn_rate=5000.0,  # Burning $5k/month
            runway_months=6.0,  # Only 6 months left!
            monetization_strategy="None - free service"
        )
        self.growth = GrowthSustainability(
            user_count=5000,  # Many users!
            growth_rate=50.0,  # Growing fast!
            cost_per_user=1.0,
            infrastructure_cost=5000.0,
            can_scale=False  # Can't scale!
        )
        self.months_operating = 0
    
    def ignore_technical_sustainability(self):
        """Ignore technical sustainability"""
        print("\n" + "=" * 70)
        print("TECHNICAL SUSTAINABILITY (NEGLECTED)")
        print("=" * 70)
        print("""
        ❌ Dependencies outdated: Last updated 2 years ago
        ❌ Security patches: Not applied
        ❌ Platform compatibility: Failing on new OS versions
        ❌ Technical debt: Accumulating
        
        Metrics:
        • Dependency Health: 35% (poor)
        • Platform Compatibility: 60% (failing)
        • Security Updates: 20% (vulnerable)
        • Obsolescence Risk: 75% (high!)
        • Technical Debt: 500 hours
        """)
        
        # Debt accumulates
        self.technical.technical_debt += 10.0
        self.technical.dependency_health = max(0, self.technical.dependency_health - 0.02)
    
    def ignore_economic_sustainability(self):
        """Ignore economic sustainability"""
        print("\n" + "=" * 70)
        print("ECONOMIC SUSTAINABILITY (NEGLECTED)")
        print("=" * 70)
        print(f"""
        ❌ No monetization: Free service
        ❌ Revenue: $0/month
        ❌ Costs: ${self.economic.costs:,.0f}/month
        ❌ Loss: ${self.economic.costs:,.0f}/month
        ❌ Runway: {self.economic.runway_months:.0f} months
        
        Problem:
        • Service is free (no revenue)
        • Costs increase with users
        • Burning through funding
        • No path to profitability
        """)
        
        # Runway decreases
        self.economic.runway_months = max(0, self.economic.runway_months - 1)
        self.economic.costs += 500  # Costs increase
    
    def unsustainable_growth(self):
        """Unsustainable growth - death by success"""
        print("\n" + "=" * 70)
        print("GROWTH SUSTAINABILITY (UNSUSTAINABLE)")
        print("=" * 70)
        print(f"""
        ⚠️  Users: {self.growth.user_count:,}
        ⚠️  Growth Rate: {self.growth.growth_rate:.0f}%/month (too fast!)
        ⚠️  Cost per User: ${self.growth.cost_per_user:.2f}
        ⚠️  Infrastructure Cost: ${self.growth.infrastructure_cost:,.0f}/month
        ❌ Can Scale: No (architecture can't handle it)
        
        Problem: "Death by Success"
        • Growing too fast
        • Costs increase linearly with users
        • Architecture can't scale
        • Infrastructure costs explode
        """)
        
        # Growth increases costs
        new_users = int(self.growth.user_count * (self.growth.growth_rate / 100))
        self.growth.user_count += new_users
        self.growth.infrastructure_cost += new_users * 1.0  # Linear cost increase
        self.growth.cost_per_user = self.growth.infrastructure_cost / self.growth.user_count if self.growth.user_count > 0 else 1.0
    
    def simulate_month(self):
        """Simulate one month of operation"""
        self.months_operating += 1
        print(f"\n{'=' * 70}")
        print(f"MONTH {self.months_operating}")
        print(f"{'=' * 70}")
        
        self.ignore_technical_sustainability()
        self.ignore_economic_sustainability()
        self.unsustainable_growth()
        
        if self.economic.runway_months <= 0:
            print("\n💀 STARTUP FAILED: Out of money!")
            return False
        return True


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_sustainability():
    """
    Demonstrate sustainability across technical, economic, and growth dimensions.
    """
    print("=" * 70)
    print("EXAMPLE 6: Sustainability - Technical, Economic, and Growth")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Technical Sustainability: Avoiding obsolescence")
    print("   • Economic Sustainability: Business viability")
    print("   • Growth Sustainability: Scaling without breaking")
    
    # Sustainable startup
    print("\n" + "=" * 70)
    print("SUSTAINABLE STARTUP")
    print("=" * 70)
    
    sustainable = SustainableStartup()
    
    print("\n📅 Simulating 6 months...")
    for month in range(6):
        sustainable.simulate_month()
    
    print("\n" + "=" * 70)
    print("SUSTAINABILITY REPORT (After 6 Months)")
    print("=" * 70)
    report = sustainable.get_sustainability_report()
    
    for dimension, metrics in report.items():
        print(f"\n{dimension.upper().replace('_', ' ')}:")
        for key, value in metrics.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Unsustainable startup
    print("\n" + "=" * 70)
    print("UNSUSTAINABLE STARTUP")
    print("=" * 70)
    
    unsustainable = UnsustainableStartup()
    
    print("\n📅 Simulating 6 months...")
    for month in range(6):
        if not unsustainable.simulate_month():
            break
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Three Dimensions of Sustainability:
    
    1. Technical Sustainability:
       • Keep dependencies updated
       • Apply security patches
       • Maintain platform compatibility
       • Manage technical debt
       • Avoid obsolescence
    
    2. Economic Sustainability:
       • Have a monetization strategy
       • Control costs
       • Achieve positive unit economics
       • Maintain sufficient runway
       • Path to profitability
    
    3. Growth Sustainability:
       • Architecture supports scaling
       • Cost per user decreases with scale
       • Can handle growth
       • Avoid "death by success"
    
    Sustainable Startup:
    ✅ All three dimensions managed
    ✅ Profitable and growing
    ✅ Can scale cost-effectively
    ✅ Long-term viability
    
    Unsustainable Startup:
    ❌ Neglects technical sustainability
    ❌ No monetization (burning money)
    ❌ Can't scale (costs explode)
    ❌ Runs out of money
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD EXAMPLE")
    print("=" * 70)
    print("""
    Startup A (Sustainable):
    • Technical: Regular updates, low debt
    • Economic: Freemium model, profitable
    • Growth: Scalable architecture, economies of scale
    • Result: Successful, growing, profitable
    
    Startup B (Unsustainable):
    • Technical: Outdated dependencies, high debt
    • Economic: Free service, no revenue, burning money
    • Growth: Can't scale, costs explode
    • Result: Failed after 6 months (out of money)
    
    "Death by Success" Scenario:
    • Service goes viral
    • Users grow 50%/month
    • But costs grow linearly
    • No monetization
    • Architecture can't scale
    • Infrastructure costs explode
    • Run out of money
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Sustainability requires balance across all dimensions:
    
    ✅ Technical: Keep technology current
    ✅ Economic: Make money and control costs
    ✅ Growth: Scale without breaking
    
    Common Mistakes:
    ❌ Focus only on technical (forget economics)
    ❌ Focus only on growth (forget economics)
    ❌ Ignore technical debt (future problems)
    ❌ No monetization strategy (burn money)
    ❌ Can't scale cost-effectively (death by success)
    
    Remember: Technical excellence alone is not enough!
    You need technical, economic, AND growth sustainability.
    """)


if __name__ == "__main__":
    demonstrate_sustainability()


