#!/usr/bin/env python3
"""
BAD EXAMPLE 4: No Sustainability - Death by Success

This demonstrates what happens when you DON'T plan for sustainability.
Compare this to example6_sustainability.py to see the difference.

PROBLEMS:
1. No technical sustainability - outdated technology
2. No economic sustainability - no monetization
3. No growth sustainability - can't scale
4. "Death by success" - success kills the business
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


# ============================================================================
# BAD: No sustainability - death by success
# ============================================================================

class UnsustainableStartup:
    """
    BAD ARCHITECTURE: No sustainability planning
    
    Problems:
    - No technical sustainability (outdated tech)
    - No economic sustainability (no revenue)
    - No growth sustainability (can't scale)
    - "Death by success" scenario
    """
    
    def __init__(self):
        # Technical sustainability - BAD
        self.dependency_version = "1.0.0"  # 2 years old!
        self.last_update = datetime.now() - timedelta(days=730)
        self.security_vulnerabilities = 15
        self.technical_debt = 800.0  # Very high!
        self.obsolescence_risk = 0.85  # High risk!
        
        # Economic sustainability - BAD
        self.revenue = 0.0  # No revenue!
        self.costs = 5000.0  # High costs!
        self.burn_rate = 5000.0  # Burning $5k/month
        self.runway_months = 6.0  # Only 6 months left!
        self.monetization_strategy = "None - free service"
        
        # Growth sustainability - BAD
        self.user_count = 10000  # Many users!
        self.growth_rate = 50.0  # Growing 50%/month!
        self.cost_per_user = 0.50
        self.infrastructure_cost = 5000.0
        self.can_scale = False  # Can't scale!
        self.months_operating = 0
    
    def ignore_technical_sustainability(self):
        """
        BAD: Ignore technical sustainability
        
        Problems:
        - Outdated dependencies
        - Security vulnerabilities
        - High obsolescence risk
        - Technical debt explodes
        """
        print("\n" + "=" * 70)
        print("TECHNICAL SUSTAINABILITY (NEGLECTED)")
        print("=" * 70)
        print(f"""
        ❌ Dependency version: {self.dependency_version} (2 years old!)
        ❌ Last update: {self.last_update.strftime('%Y-%m-%d')}
        ❌ Security vulnerabilities: {self.security_vulnerabilities}
        ❌ Technical debt: {self.technical_debt:.0f} hours
        ❌ Obsolescence risk: {self.obsolescence_risk * 100:.0f}%
        
        Problems:
        • Can't use new features
        • Security risks
        • Compatibility issues
        • High maintenance cost
        """)
        
        # Problems get worse
        self.security_vulnerabilities += 1
        self.technical_debt += 20.0
        self.obsolescence_risk = min(1.0, self.obsolescence_risk + 0.02)
    
    def ignore_economic_sustainability(self):
        """
        BAD: Ignore economic sustainability
        
        Problems:
        - No revenue
        - High costs
        - Burning money
        - No path to profitability
        """
        print("\n" + "=" * 70)
        print("ECONOMIC SUSTAINABILITY (NEGLECTED)")
        print("=" * 70)
        print(f"""
        ❌ Revenue: ${self.revenue:,.0f}/month (ZERO!)
        ❌ Costs: ${self.costs:,.0f}/month
        ❌ Loss: ${self.costs:,.0f}/month
        ❌ Burn rate: ${self.burn_rate:,.0f}/month
        ❌ Runway: {self.runway_months:.0f} months
        ❌ Monetization: {self.monetization_strategy}
        
        Problems:
        • No revenue model
        • Costs increase with users
        • Burning through funding
        • No path to profitability
        """)
        
        # Runway decreases
        self.runway_months = max(0, self.runway_months - 1)
        # Costs increase with users
        self.costs += 200
    
    def unsustainable_growth(self):
        """
        BAD: Unsustainable growth - "death by success"
        
        Problems:
        - Growing too fast
        - Costs increase linearly
        - Can't scale architecture
        - Infrastructure costs explode
        """
        print("\n" + "=" * 70)
        print("GROWTH SUSTAINABILITY (UNSUSTAINABLE)")
        print("=" * 70)
        print(f"""
        ⚠️  Users: {self.user_count:,}
        ⚠️  Growth: {self.growth_rate:.0f}%/month (too fast!)
        ⚠️  Cost per user: ${self.cost_per_user:.2f}
        ⚠️  Infrastructure: ${self.infrastructure_cost:,.0f}/month
        ❌ Can scale: No (architecture can't handle it)
        
        "Death by Success" Scenario:
        • Service goes viral
        • Users grow 50%/month
        • But costs grow linearly
        • Architecture can't scale
        • Infrastructure costs explode
        • No revenue to pay for it
        """)
        
        # Growth increases costs linearly (bad!)
        new_users = int(self.user_count * (self.growth_rate / 100))
        self.user_count += new_users
        # Linear cost increase (bad architecture!)
        self.infrastructure_cost += new_users * 0.50
        self.cost_per_user = self.infrastructure_cost / self.user_count if self.user_count > 0 else 0.50
        # Costs increase
        self.costs = self.infrastructure_cost
    
    def simulate_month(self):
        """Simulate one month"""
        self.months_operating += 1
        print(f"\n{'=' * 70}")
        print(f"MONTH {self.months_operating}")
        print(f"{'=' * 70}")
        
        self.ignore_technical_sustainability()
        self.ignore_economic_sustainability()
        self.unsustainable_growth()
        
        if self.runway_months <= 0:
            print("\n💀 STARTUP FAILED: Out of money!")
            print(f"   Users: {self.user_count:,}")
            print(f"   Costs: ${self.costs:,.0f}/month")
            print(f"   Revenue: ${self.revenue:,.0f}/month")
            print("   Reason: 'Death by success' - grew too fast without monetization")
            return False
        return True
    
    def get_sustainability_report(self):
        """Get sustainability report (but it's terrible!)"""
        return {
            "technical": {
                "dependency_version": self.dependency_version,
                "security_vulnerabilities": self.security_vulnerabilities,
                "technical_debt": f"{self.technical_debt:.0f} hours",
                "obsolescence_risk": f"{self.obsolescence_risk * 100:.0f}%"
            },
            "economic": {
                "revenue": f"${self.revenue:,.0f}/month",
                "costs": f"${self.costs:,.0f}/month",
                "loss": f"${self.costs:,.0f}/month",
                "runway": f"{self.runway_months:.0f} months",
                "monetization": self.monetization_strategy
            },
            "growth": {
                "users": f"{self.user_count:,}",
                "growth_rate": f"{self.growth_rate:.0f}%/month",
                "cost_per_user": f"${self.cost_per_user:.2f}",
                "can_scale": "No"
            }
        }


# ============================================================================
# DEMONSTRATION: Why This Is Bad
# ============================================================================

def demonstrate_no_sustainability():
    """
    Demonstrate the problems with no sustainability
    """
    print("=" * 70)
    print("BAD EXAMPLE 4: No Sustainability - Death by Success")
    print("=" * 70)
    print("\n❌ PROBLEMS WITH NO SUSTAINABILITY:")
    print("   1. No technical sustainability - outdated technology")
    print("   2. No economic sustainability - no monetization")
    print("   3. No growth sustainability - can't scale")
    print("   4. 'Death by success' - success kills the business")
    
    startup = UnsustainableStartup()
    
    print("\n" + "=" * 70)
    print("INITIAL STATE")
    print("=" * 70)
    report = startup.get_sustainability_report()
    for dimension, metrics in report.items():
        print(f"\n{dimension.upper().replace('_', ' ')}:")
        for key, value in metrics.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    print("SIMULATING 6 MONTHS")
    print("=" * 70)
    
    # Simulate months until failure
    for month in range(6):
        if not startup.simulate_month():
            break
    
    print("\n" + "=" * 70)
    print("SCENARIO: Service Goes Viral")
    print("=" * 70)
    print("""
    Service goes viral - 50% growth per month!
    
    Month 1: 10,000 users
    Month 2: 15,000 users
    Month 3: 22,500 users
    Month 4: 33,750 users
    Month 5: 50,625 users
    Month 6: 75,937 users
    
    But:
    • No revenue (free service)
    • Costs increase linearly
    • Can't scale architecture
    • Infrastructure costs explode
    
    Result: "Death by success" - success kills the business!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: Technical Debt Accumulates")
    print("=" * 70)
    print("""
    Technical sustainability ignored:
    
    • Dependencies 2 years old
    • 15+ security vulnerabilities
    • 800+ hours technical debt
    • 85% obsolescence risk
    
    Problems:
    • Can't use new features
    • Security risks
    • High maintenance cost
    • Must rewrite soon
    
    Result: Technical debt makes system unmaintainable!
    """)
    
    print("\n" + "=" * 70)
    print("SCENARIO: No Monetization")
    print("=" * 70)
    print("""
    Economic sustainability ignored:
    
    • No revenue model
    • Free service
    • Costs: $5,000/month
    • Runway: 6 months
    
    Problems:
    • Burning through funding
    • No path to profitability
    • Can't sustain growth
    • Will run out of money
    
    Result: Startup fails even with many users!
    """)
    
    print("\n" + "=" * 70)
    print("COMPARE TO: Sustainable Startup (example6_sustainability.py)")
    print("=" * 70)
    print("""
    With sustainability:
    
    ✅ Technical: Regular updates, low debt
    ✅ Economic: Freemium model, profitable
    ✅ Growth: Scalable architecture, economies of scale
    
    Result:
    • Profitable and growing
    • Can scale cost-effectively
    • Long-term viability
    """)
    
    print("\n" + "=" * 70)
    print("REAL-WORLD IMPACT")
    print("=" * 70)
    print("""
    Unsustainable startup:
    
    • Technical: Outdated, vulnerable, high debt
    • Economic: No revenue, burning money
    • Growth: Can't scale, costs explode
    
    After 6 months:
    • 75,000+ users (success!)
    • $30,000+/month costs
    • $0 revenue
    • Out of money
    • Startup fails
    
    Cost:
    • $180,000+ burned
    • Lost opportunity
    • Team demoralized
    • Users disappointed
    
    With sustainability:
    • Profitable from month 3
    • Can scale cost-effectively
    • Long-term success
    """)


if __name__ == "__main__":
    demonstrate_no_sustainability()


