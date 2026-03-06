# Lecture 2: Quality Attributes

## Overview

This folder contains practical Python examples demonstrating key concepts from Chapter 2: Quality Attributes.

Quality attributes are the non-functional requirements that determine how well a software system performs its functions. They are the reason why we need software architecture - quality must be designed into the system from the beginning.

## Learning Objectives

By working through these examples, you will understand:

1. **Internal vs. External Quality** - Developer experience vs. user experience
2. **Static vs. Dynamic Quality** - Structural properties vs. runtime behavior
3. **Meta-Qualities** - Observability, measurability, testability, and more
4. **Quality Attributes Across Lifecycle** - Design, operation, failure, attack, change, and long-term
5. **Maintainability** - Corrective, adaptive, perfective, and preventive maintenance
6. **Sustainability** - Technical, economic, and growth sustainability

## Example Files

### `example1_internal_vs_external_quality.py`
**Concepts:** Internal Quality, External Quality, Developer Experience, User Experience
- Demonstrates the difference between code quality (internal) and user experience (external)
- Shows how internal quality affects external quality over time
- Real-world example: E-commerce platform

### `example2_static_vs_dynamic_quality.py`
**Concepts:** Static Quality, Dynamic Quality, Structural Properties, Runtime Behavior
- Static qualities: complexity, coupling, test coverage (measured before deployment)
- Dynamic qualities: performance, availability, reliability (measured during operation)
- Real-world example: Web application architecture

### `example3_meta_qualities.py`
**Concepts:** Observability, Measurability, Repeatability, Predictability, Auditability, Accountability, Testability
- How to observe and measure quality attributes
- Making quality attributes measurable and repeatable
- Real-world example: Monitoring and observability system

### `example4_quality_lifecycle.py`
**Concepts:** Quality in Design, Operation, Failure, Attack, Change, Long-term
- How quality attributes manifest at different stages
- Handling failures, attacks, and changes
- Real-world example: Banking system

### `example5_maintainability.py`
**Concepts:** Corrective, Adaptive, Perfective, Preventive Maintenance
- Four types of maintenance and when to use each
- Balancing maintenance types for sustainable development
- Real-world example: Legacy system evolution

### `example6_sustainability.py`
**Concepts:** Technical Sustainability, Economic Sustainability, Growth Sustainability
- Avoiding technical obsolescence
- Economic viability and monetization
- Sustainable growth strategies
- Real-world example: Startup to scale-up journey

## Key Concepts

### Internal vs. External Quality

**Internal Quality** (Developer-facing):
- Code readability and maintainability
- Test coverage
- Documentation quality
- Architecture clarity
- Development velocity

**External Quality** (User-facing):
- Performance and responsiveness
- Availability and reliability
- Security
- Usability
- Feature completeness

### Static vs. Dynamic Quality

**Static Quality** (Measurable before deployment):
- Code complexity (cyclomatic complexity)
- Coupling and cohesion
- Test coverage percentage
- Architecture compliance
- Code smells

**Dynamic Quality** (Measurable during operation):
- Response time and throughput
- Availability percentage
- Error rates
- Resource utilization
- User satisfaction

### Meta-Qualities

Before measuring any quality attribute, ask:
- **Observability**: Can we see it?
- **Measurability**: Can we quantify it?
- **Repeatability**: Do we get consistent results?
- **Predictability**: Can we forecast it?
- **Auditability**: Can we verify it?
- **Accountability**: Who is responsible?
- **Testability**: Can we test it?

### Quality Attributes Across Lifecycle

1. **Design**: Architecture decisions affect future quality
2. **Operation**: System behavior under normal conditions
3. **Failure**: How system handles errors and failures
4. **Attack**: Security and resilience to attacks
5. **Change**: How system adapts to new requirements
6. **Long-term**: Sustainability and evolution over years

### Types of Maintenance

- **Corrective**: Fix bugs and defects
- **Adaptive**: Adapt to external changes (OS, libraries, platforms)
- **Perfective**: Improve external qualities (performance, features)
- **Preventive**: Improve internal qualities (refactoring, code quality)

### Sustainability

- **Technical**: Avoid obsolescence, manage dependencies
- **Economic**: Monetization, cost management, business viability
- **Growth**: Sustainable scaling, avoid "death by success"

## Running the Examples

### Good Architecture Examples

```bash
# Run all examples
python3 example1_internal_vs_external_quality.py
python3 example2_static_vs_dynamic_quality.py
python3 example3_meta_qualities.py
python3 example4_quality_lifecycle.py
python3 example5_maintainability.py
python3 example6_sustainability.py
```

### Bad Architecture Examples (Learn from Mistakes!)

```bash
# See what happens when you ignore internal quality
python3 bad_examples/bad_example1_no_internal_quality.py

# See what happens when you ignore observability
python3 bad_examples/bad_example2_no_observability.py

# See what happens when you ignore maintainability
python3 bad_examples/bad_example3_no_maintainability.py

# See what happens when you ignore sustainability
python3 bad_examples/bad_example4_no_sustainability.py
```

Compare the bad examples to the good examples to understand the difference!

## Business Examples

Each example includes real-world business scenarios:
- **E-commerce Platform**: Internal code quality vs. external user experience
- **Web Application**: Static analysis vs. dynamic performance
- **Monitoring System**: Observability and measurability
- **Banking System**: Quality across lifecycle (operation, failure, attack)
- **Legacy System**: Maintenance strategies
- **Startup Journey**: Sustainability challenges

## Quality Attribute Trade-offs

Remember: Quality attributes often compete with each other:
- **Performance vs. Maintainability**: Optimized code may be harder to maintain
- **Security vs. Usability**: More security can reduce usability
- **Cost vs. Quality**: Higher quality often costs more
- **Speed vs. Reliability**: Faster delivery may reduce reliability

The architect's job is to balance these trade-offs based on business priorities.

## Next Steps

After understanding these concepts, you'll be able to:
- Identify and prioritize quality attributes for your system
- Design architecture that supports required quality attributes
- Measure and monitor quality attributes
- Make informed trade-offs between competing qualities
- Plan for long-term sustainability


