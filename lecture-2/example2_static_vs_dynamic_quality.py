#!/usr/bin/env python3
"""
Example 2: Static vs. Dynamic Quality Attributes

This example demonstrates:
- Static quality: Measurable before deployment (code analysis)
- Dynamic quality: Measurable during operation (runtime behavior)
- How static quality predicts dynamic quality
- Real-world business scenario: Web Application

Key Concept: Static qualities can be measured by analyzing code.
Dynamic qualities can only be measured when the system is running.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
import random


# ============================================================================
# BUSINESS SCENARIO: Web Application
# ============================================================================
# Static quality: Code complexity, coupling, test coverage
# Dynamic quality: Response time, throughput, availability
# Good static quality often leads to good dynamic quality.
#


@dataclass
class StaticQualityMetrics:
    """Static quality metrics (measurable before deployment)"""
    cyclomatic_complexity: float  # Code complexity
    coupling_score: float  # 0-1, lower is better
    cohesion_score: float  # 0-1, higher is better
    test_coverage: float  # 0-1
    code_smells: int  # Number of code smells
    architecture_compliance: float  # 0-1
    dependency_count: int  # Number of dependencies


@dataclass
class DynamicQualityMetrics:
    """Dynamic quality metrics (measurable during operation)"""
    average_response_time: float  # Seconds
    p95_response_time: float  # 95th percentile
    throughput: float  # Requests per second
    error_rate: float  # 0-1
    availability: float  # 0-1
    cpu_usage: float  # 0-1
    memory_usage: float  # 0-1


# ============================================================================
# SYSTEM WITH GOOD STATIC QUALITY
# ============================================================================

class WellStructuredWebApp:
    """
    Web application with good static quality.
    
    Static Quality (Code Analysis):
    ✅ Low complexity
    ✅ Low coupling
    ✅ High cohesion
    ✅ High test coverage
    ✅ Few code smells
    
    Dynamic Quality (Runtime):
    ✅ Fast response times
    ✅ High throughput
    ✅ Low error rate
    ✅ High availability
    """
    
    def __init__(self):
        self.static_quality = StaticQualityMetrics(
            cyclomatic_complexity=4.2,  # Low complexity
            coupling_score=0.15,  # Low coupling
            cohesion_score=0.85,  # High cohesion
            test_coverage=0.88,  # 88% coverage
            code_smells=3,  # Few smells
            architecture_compliance=0.92,
            dependency_count=12  # Reasonable dependencies
        )
        self.dynamic_quality = DynamicQualityMetrics(
            average_response_time=0.12,  # 120ms
            p95_response_time=0.25,  # 250ms
            throughput=850.0,  # 850 req/s
            error_rate=0.001,  # 0.1% errors
            availability=0.9995,  # 99.95% uptime
            cpu_usage=0.35,  # 35% CPU
            memory_usage=0.42  # 42% memory
        )
    
    def handle_request(self, request_type: str) -> Dict:
        """Handle a request - fast because of good structure"""
        start_time = time.time()
        
        # Simulate processing
        # Low complexity = fast execution
        processing_time = 0.08 + random.uniform(0, 0.05)
        time.sleep(processing_time)
        
        response_time = time.time() - start_time
        
        # Low error rate due to good test coverage
        error = random.random() < self.dynamic_quality.error_rate
        
        return {
            "success": not error,
            "response_time": response_time,
            "request_type": request_type
        }
    
    def get_static_analysis_report(self) -> Dict:
        """Get static analysis report"""
        return {
            "cyclomatic_complexity": self.static_quality.cyclomatic_complexity,
            "coupling": f"{self.static_quality.coupling_score * 100:.1f}%",
            "cohesion": f"{self.static_quality.cohesion_score * 100:.1f}%",
            "test_coverage": f"{self.static_quality.test_coverage * 100:.1f}%",
            "code_smells": self.static_quality.code_smells,
            "architecture_compliance": f"{self.static_quality.architecture_compliance * 100:.1f}%"
        }
    
    def get_dynamic_metrics(self) -> Dict:
        """Get dynamic runtime metrics"""
        return {
            "avg_response_time": f"{self.dynamic_quality.average_response_time * 1000:.0f}ms",
            "p95_response_time": f"{self.dynamic_quality.p95_response_time * 1000:.0f}ms",
            "throughput": f"{self.dynamic_quality.throughput:.0f} req/s",
            "error_rate": f"{self.dynamic_quality.error_rate * 100:.2f}%",
            "availability": f"{self.dynamic_quality.availability * 100:.2f}%",
            "cpu_usage": f"{self.dynamic_quality.cpu_usage * 100:.0f}%",
            "memory_usage": f"{self.dynamic_quality.memory_usage * 100:.0f}%"
        }


# ============================================================================
# SYSTEM WITH POOR STATIC QUALITY
# ============================================================================

class PoorlyStructuredWebApp:
    """
    Web application with poor static quality.
    
    Static Quality (Code Analysis):
    ❌ High complexity
    ❌ High coupling
    ❌ Low cohesion
    ❌ Low test coverage
    ❌ Many code smells
    
    Dynamic Quality (Runtime):
    ❌ Slower response times
    ❌ Lower throughput
    ❌ Higher error rate
    ❌ Lower availability
    """
    
    def __init__(self):
        self.static_quality = StaticQualityMetrics(
            cyclomatic_complexity=28.5,  # High complexity
            coupling_score=0.75,  # High coupling
            cohesion_score=0.25,  # Low cohesion
            test_coverage=0.18,  # Only 18% coverage
            code_smells=47,  # Many smells
            architecture_compliance=0.35,
            dependency_count=87  # Too many dependencies
        )
        self.dynamic_quality = DynamicQualityMetrics(
            average_response_time=0.85,  # 850ms (7x slower!)
            p95_response_time=2.1,  # 2.1s
            throughput=120.0,  # 120 req/s (7x lower!)
            error_rate=0.045,  # 4.5% errors (45x worse!)
            availability=0.985,  # 98.5% uptime
            cpu_usage=0.78,  # 78% CPU (high!)
            memory_usage=0.85  # 85% memory (high!)
        )
    
    def handle_request(self, request_type: str) -> Dict:
        """Handle a request - slow because of poor structure"""
        start_time = time.time()
        
        # Simulate processing
        # High complexity = slow execution
        processing_time = 0.6 + random.uniform(0, 0.3)
        time.sleep(processing_time)
        
        response_time = time.time() - start_time
        
        # High error rate due to low test coverage
        error = random.random() < self.dynamic_quality.error_rate
        
        return {
            "success": not error,
            "response_time": response_time,
            "request_type": request_type
        }
    
    def get_static_analysis_report(self) -> Dict:
        """Get static analysis report"""
        return {
            "cyclomatic_complexity": self.static_quality.cyclomatic_complexity,
            "coupling": f"{self.static_quality.coupling_score * 100:.1f}%",
            "cohesion": f"{self.static_quality.cohesion_score * 100:.1f}%",
            "test_coverage": f"{self.static_quality.test_coverage * 100:.1f}%",
            "code_smells": self.static_quality.code_smells,
            "architecture_compliance": f"{self.static_quality.architecture_compliance * 100:.1f}%"
        }
    
    def get_dynamic_metrics(self) -> Dict:
        """Get dynamic runtime metrics"""
        return {
            "avg_response_time": f"{self.dynamic_quality.average_response_time * 1000:.0f}ms",
            "p95_response_time": f"{self.dynamic_quality.p95_response_time * 1000:.0f}ms",
            "throughput": f"{self.dynamic_quality.throughput:.0f} req/s",
            "error_rate": f"{self.dynamic_quality.error_rate * 100:.2f}%",
            "availability": f"{self.dynamic_quality.availability * 100:.2f}%",
            "cpu_usage": f"{self.dynamic_quality.cpu_usage * 100:.0f}%",
            "memory_usage": f"{self.dynamic_quality.memory_usage * 100:.0f}%"
        }


# ============================================================================
# STATIC ANALYSIS TOOL
# ============================================================================

class StaticAnalysisTool:
    """
    Simulates static analysis tools (SonarQube, CodeClimate, etc.)
    that measure static quality before deployment.
    """
    
    @staticmethod
    def analyze(app) -> Dict:
        """Analyze static quality of application"""
        print("\n" + "=" * 70)
        print("STATIC ANALYSIS REPORT (Measurable Before Deployment)")
        print("=" * 70)
        
        report = app.get_static_analysis_report()
        
        print("\n📊 Code Metrics:")
        for metric, value in report.items():
            print(f"   {metric.replace('_', ' ').title()}: {value}")
        
        # Predict dynamic quality based on static quality
        print("\n🔮 Predicted Dynamic Quality:")
        if isinstance(app, WellStructuredWebApp):
            print("   ✅ Low complexity → Fast response times")
            print("   ✅ High test coverage → Low error rate")
            print("   ✅ Low coupling → High maintainability")
            print("   ✅ Good architecture → High availability")
        else:
            print("   ⚠️  High complexity → Slow response times")
            print("   ⚠️  Low test coverage → High error rate")
            print("   ⚠️  High coupling → Low maintainability")
            print("   ⚠️  Poor architecture → Lower availability")
        
        return report


# ============================================================================
# DYNAMIC MONITORING TOOL
# ============================================================================

class DynamicMonitoringTool:
    """
    Simulates monitoring tools (Prometheus, Datadog, etc.)
    that measure dynamic quality during operation.
    """
    
    @staticmethod
    def monitor(app, num_requests: int = 100):
        """Monitor dynamic quality during operation"""
        print("\n" + "=" * 70)
        print(f"DYNAMIC MONITORING REPORT (Measured During Operation)")
        print("=" * 70)
        print(f"\n📈 Simulating {num_requests} requests...")
        
        response_times = []
        errors = 0
        
        for i in range(num_requests):
            result = app.handle_request(f"request_{i}")
            response_times.append(result["response_time"])
            if not result["success"]:
                errors += 1
        
        avg_response = sum(response_times) / len(response_times)
        p95_index = int(len(response_times) * 0.95)
        p95_response = sorted(response_times)[p95_index]
        
        print(f"\n📊 Runtime Metrics:")
        metrics = app.get_dynamic_metrics()
        for metric, value in metrics.items():
            print(f"   {metric.replace('_', ' ').title()}: {value}")
        
        print(f"\n   Measured Avg Response: {avg_response * 1000:.0f}ms")
        print(f"   Measured P95 Response: {p95_response * 1000:.0f}ms")
        print(f"   Measured Errors: {errors}/{num_requests} ({errors/num_requests*100:.1f}%)")
        
        return metrics


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_static_vs_dynamic_quality():
    """
    Demonstrate the difference between static and dynamic quality.
    """
    print("=" * 70)
    print("EXAMPLE 2: Static vs. Dynamic Quality Attributes")
    print("=" * 70)
    print("\n📚 Key Concepts:")
    print("   • Static Quality: Measurable before deployment (code analysis)")
    print("   • Dynamic Quality: Measurable during operation (runtime metrics)")
    print("   • Static quality often predicts dynamic quality")
    print("   • Both are important for system success")
    
    # Create applications
    good_app = WellStructuredWebApp()
    bad_app = PoorlyStructuredWebApp()
    
    print("\n" + "=" * 70)
    print("COMPARISON: Good vs. Poor Static Quality")
    print("=" * 70)
    
    # Analyze static quality
    print("\n" + "🔍 WELL-STRUCTURED APPLICATION")
    StaticAnalysisTool.analyze(good_app)
    DynamicMonitoringTool.monitor(good_app, num_requests=50)
    
    print("\n" + "🔍 POORLY-STRUCTURED APPLICATION")
    StaticAnalysisTool.analyze(bad_app)
    DynamicMonitoringTool.monitor(bad_app, num_requests=50)
    
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print("""
    Static Quality (Code Analysis):
    
    Well-Structured:
    ✅ Complexity: 4.2 (low)
    ✅ Coupling: 15% (low)
    ✅ Test Coverage: 88% (high)
    ✅ Code Smells: 3 (few)
    
    Poorly-Structured:
    ❌ Complexity: 28.5 (high - 7x worse!)
    ❌ Coupling: 75% (high)
    ❌ Test Coverage: 18% (low)
    ❌ Code Smells: 47 (many - 15x worse!)
    
    Dynamic Quality (Runtime):
    
    Well-Structured:
    ✅ Response Time: 120ms (fast)
    ✅ Throughput: 850 req/s (high)
    ✅ Error Rate: 0.1% (low)
    ✅ Availability: 99.95% (high)
    
    Poorly-Structured:
    ❌ Response Time: 850ms (7x slower!)
    ❌ Throughput: 120 req/s (7x lower!)
    ❌ Error Rate: 4.5% (45x worse!)
    ❌ Availability: 98.5% (lower)
    
    Correlation:
    • Low complexity → Fast response times
    • High test coverage → Low error rate
    • Low coupling → Better maintainability
    • Good architecture → High availability
    """)
    
    print("\n" + "=" * 70)
    print("WHEN TO MEASURE")
    print("=" * 70)
    print("""
    Static Quality (Before Deployment):
    ✅ Measure during development
    ✅ Use CI/CD to check on every commit
    ✅ Catch problems early (cheaper to fix)
    ✅ Tools: SonarQube, CodeClimate, ESLint, Pylint
    
    Dynamic Quality (During Operation):
    ✅ Measure in production
    ✅ Monitor continuously
    ✅ Set up alerts for thresholds
    ✅ Tools: Prometheus, Datadog, New Relic, CloudWatch
    
    Best Practice:
    1. Measure static quality early and often
    2. Use static quality to predict dynamic quality
    3. Monitor dynamic quality in production
    4. Fix static quality issues to improve dynamic quality
    """)
    
    print("\n" + "=" * 70)
    print("TAKEAWAY")
    print("=" * 70)
    print("""
    Static and dynamic quality are related:
    
    ✅ Good static quality → Good dynamic quality
    ❌ Poor static quality → Poor dynamic quality
    
    Measure both:
    • Static quality: Catch problems early
    • Dynamic quality: Verify in production
    
    Remember: You can't measure dynamic quality until you deploy,
    but you can predict it from static quality!
    """)


if __name__ == "__main__":
    demonstrate_static_vs_dynamic_quality()

