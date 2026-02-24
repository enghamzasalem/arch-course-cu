# Lecture 1: Exercises - Introduction to Software Architecture

## Overview

These exercises are designed to reinforce the key concepts from Lecture 1:
- Abstraction and Interfaces
- Modularity and Components
- Architecture as Communication
- Quality Attributes and Trade-offs
- Evolution and Change

## Exercise Difficulty Levels

- 🟢 **Beginner**: Basic understanding required
- 🟡 **Intermediate**: Some experience helpful
- 🔴 **Advanced**: Requires deeper understanding

---

## EXERCISE SET 1: Abstraction and Interfaces

### Exercise 1.1: Create a Storage Abstraction 🟢

**Objective**: Practice creating abstract interfaces and multiple implementations.

**Task**: 
Create an abstract `Storage` interface that can work with different storage backends (local file system, cloud storage, database).

**Requirements**:
1. Define an abstract `Storage` interface with methods:
   - `save(key: str, data: bytes) -> bool`
   - `load(key: str) -> bytes`
   - `delete(key: str) -> bool`
   - `exists(key: str) -> bool`

2. Implement at least two concrete classes:
   - `FileSystemStorage`: Stores files on local disk
   - `InMemoryStorage`: Stores data in memory (for testing)

3. Create a `DocumentManager` class that uses the `Storage` interface (not specific implementations)

4. Demonstrate that you can swap storage backends without changing `DocumentManager`

**Deliverables**:
- `exercise1_1_storage_abstraction.py`
- Brief explanation of how abstraction helps in this scenario

**Learning Goals**:
- Understand interface design
- Practice dependency injection
- See the benefits of abstraction

---

### Exercise 1.2: Refactor Bad Code to Use Abstraction 🟡

**Objective**: Practice refactoring tightly coupled code to use abstraction.

**Task**:
You're given a `NotificationService` class that directly calls the SendGrid email API:

```python
class NotificationService:
    def __init__(self):
        self.sendgrid_api_key = "SG.xxx"
        self.sendgrid_url = "https://api.sendgrid.com/v3"
    
    def send_email(self, to: str, subject: str, body: str):
        # Direct SendGrid API calls
        import requests
        response = requests.post(
            f"{self.sendgrid_url}/mail/send",
            headers={"Authorization": f"Bearer {self.sendgrid_api_key}"},
            json={"personalizations": [...], "from": {...}, "content": [...]}
        )
        # ... SendGrid-specific code
```

**Requirements**:
1. Create an abstract `EmailProvider` interface
2. Implement `SendGridEmailProvider` (wraps existing code)
3. Implement `MockEmailProvider` (for testing)
4. Refactor `NotificationService` to use the interface
5. Show that you can now test without real API calls

**Deliverables**:
- `exercise1_2_refactor_notification.py`
- Before/after comparison
- Explanation of improvements

**Learning Goals**:
- Refactoring skills
- Understanding vendor lock-in problems
- Testing benefits of abstraction

---

### Exercise 1.3: Design a Plugin System 🔴

**Objective**: Design a system that allows plugins using abstraction.

**Task**:
Design a text processing system that can use different plugins for:
- Text formatting (Markdown, HTML, Plain text)
- Text analysis (word count, sentiment, readability)
- Text transformation (translate, summarize, encrypt)

**Requirements**:
1. Create abstract interfaces for each plugin type
2. Implement at least 2 plugins for each type
3. Create a `TextProcessor` that can use any combination of plugins
4. Demonstrate that new plugins can be added without modifying existing code

**Deliverables**:
- `exercise1_3_plugin_system.py`
- Architecture diagram showing plugin relationships
- Documentation explaining the plugin architecture

**Learning Goals**:
- Advanced abstraction patterns
- Extensibility design
- Plugin architecture

---

## EXERCISE SET 2: Modularity and Components

### Exercise 2.1: Break Down a Monolithic System 🟢

**Objective**: Practice identifying and separating concerns.

**Task**:
You have a monolithic `LibrarySystem` class that does everything:

```python
class LibrarySystem:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.loans = {}
        self.fines = {}
        self.notifications = []
    
    def add_book(self, ...):  # Book management
    def register_member(self, ...):  # Member management
    def borrow_book(self, ...):  # Loan management
    def calculate_fine(self, ...):  # Fine calculation
    def send_notification(self, ...):  # Notification
    # ... 20 more methods mixing all concerns
```

**Requirements**:
1. Identify at least 4 distinct components (e.g., BookManager, MemberManager, LoanManager, FineCalculator)
2. Separate the monolithic class into independent components
3. Create a `LibrarySystem` orchestrator that composes these components
4. Ensure components can be tested independently

**Deliverables**:
- `exercise2_1_modular_library.py`
- Component diagram
- Explanation of separation of concerns

**Learning Goals**:
- Identifying responsibilities
- Component design
- Separation of concerns

---

### Exercise 2.2: Design a Modular E-commerce System 🟡

**Objective**: Design a system from scratch using modularity principles.

**Task**:
Design an e-commerce system with the following features:
- Product catalog
- Shopping cart
- Order processing
- Payment processing
- Inventory management
- Shipping calculation
- Customer notifications

**Requirements**:
1. Design at least 6 independent components
2. Define clear interfaces between components
3. Show how components communicate
4. Ensure components can be developed/tested independently
5. Create a main system that orchestrates components

**Deliverables**:
- `exercise2_2_ecommerce_system.py`
- Architecture diagram showing components and relationships
- Interface definitions for each component
- Brief explanation of design decisions

**Learning Goals**:
- System design from scratch
- Component identification
- Interface design
- System composition

---

 

---

## EXERCISE SET 3: Architecture as Communication

### Exercise 3.1: Document a Simple System 🟢

**Objective**: Practice creating architecture documentation.

**Task**:
Choose a simple system (e.g., a todo app, blog system, or chat application) and create architecture documentation.

**Requirements**:
1. Create at least 3 different views:
   - Logical view (what the system does)
   - Component view (what components exist)
   - Deployment view (how it's deployed)

2. For each view, create:
   - A diagram (ASCII art or description)
   - A written explanation
   - Key components/relationships

**Deliverables**:
- `exercise3_1_architecture_docs.md`
- Diagrams for each view
- Written explanations

**Learning Goals**:
- Architecture documentation
- Multiple viewpoints
- Communication through diagrams

---

### Exercise 3.2: Create Architecture Views for Different Audiences 🟡

**Objective**: Practice tailoring architecture communication for different stakeholders.

**Task**:
Take the e-commerce system from Exercise 2.2 and create architecture views for:

1. **Business Stakeholders**: Focus on business capabilities and value
2. **Developers**: Focus on technical components and code structure
3. **DevOps**: Focus on deployment and infrastructure
4. **Product Managers**: Focus on features and user flows

**Requirements**:
1. Create appropriate diagrams for each audience
2. Use language and detail level appropriate for each audience
3. Highlight what matters to each stakeholder
4. Show how the same system can be viewed differently

**Deliverables**:
- `exercise3_2_stakeholder_views.md`
- 4 different architecture views
- Explanation of how each view serves its audience

**Learning Goals**:
- Audience-aware communication
- Multiple viewpoints
- Stakeholder management

---

### Exercise 3.3: Reverse Engineer and Document Architecture 🔴

**Objective**: Practice understanding and documenting existing systems.

**Task**:
Choose an open-source project or a system you're familiar with. Reverse engineer its architecture and create comprehensive documentation.

**Requirements**:
1. Analyze the codebase to understand:
   - Component structure
   - Dependencies
   - Communication patterns
   - Data flow

2. Create documentation including:
   - System overview
   - Component diagram
   - Data flow diagram
   - Deployment architecture
   - Key design decisions

3. Identify:
   - Good architectural patterns
   - Potential improvements
   - Areas of technical debt

**Deliverables**:
- `exercise3_3_reverse_engineered_architecture.md`
- Architecture diagrams
- Analysis and recommendations

**Learning Goals**:
- System analysis
- Architecture documentation
- Critical evaluation

---

## EXERCISE SET 4: Quality Attributes and Trade-offs

### Exercise 4.1: Identify Quality Attributes 🟢

**Objective**: Practice identifying quality attributes in real systems.

**Task**:
For each of these systems, identify the top 3 quality attributes they prioritize:

1. Real-time multiplayer game
2. Banking system
3. Social media platform
4. E-commerce website
5. IoT sensor network

**Requirements**:
1. For each system, list:
   - Top 3 quality attributes
   - Why these are important
   - What trade-offs might be made

2. Explain how prioritizing different attributes would change the architecture

**Deliverables**:
- `exercise4_1_quality_attributes.md`
- Table or document with analysis
- Trade-off explanations

**Learning Goals**:
- Quality attribute identification
- Understanding priorities
- Trade-off awareness

---

### Exercise 4.2: Design for Different Quality Attributes 🟡

**Objective**: Design the same system optimized for different quality attributes.

**Task**:
Design a file storage system optimized for:

1. **Performance**: Fast read/write operations
2. **Cost**: Minimal infrastructure costs
3. **Reliability**: High availability and data durability
4. **Scalability**: Handle millions of files

**Requirements**:
1. For each optimization target:
   - Design the architecture
   - Explain key decisions
   - Identify trade-offs made
   - Estimate costs/performance

2. Compare the four architectures:
   - What's different?
   - What's the same?
   - Which would you choose and why?

**Deliverables**:
- `exercise4_2_quality_tradeoffs.py` (code implementations)
- `exercise4_2_quality_tradeoffs.md` (analysis document)
- Architecture diagrams for each approach
- Comparison table

**Learning Goals**:
- Quality attribute-driven design
- Trade-off analysis
- Decision making

---

### Exercise 4.3: Analyze Real-World Trade-offs 🔴

**Objective**: Analyze trade-offs in real systems.

**Task**:
Research and analyze a real-world system (e.g., Netflix, Amazon, Google Search) and identify:

1. **Quality Attributes**: What they prioritize
2. **Trade-offs**: What they sacrificed for their priorities
3. **Architectural Decisions**: How architecture supports their priorities
4. **Evolution**: How priorities changed over time

**Requirements**:
1. Choose a well-documented system
2. Research their architecture and decisions
3. Create an analysis document covering:
   - Quality attribute priorities
   - Trade-offs made
   - Architectural patterns used
   - Evolution over time
   - Lessons learned

**Deliverables**:
- `exercise4_3_real_world_analysis.md`
- Detailed analysis document
- References to sources

**Learning Goals**:
- Real-world architecture analysis
- Trade-off evaluation
- Learning from industry

---

## EXERCISE SET 5: Evolution and Change

### Exercise 5.1: Plan System Evolution 🟢

**Objective**: Practice planning for system evolution.

**Task**:
Design a simple blog system and plan how it would evolve through 3 stages:

1. **MVP**: 100 users, basic features
2. **Growth**: 10,000 users, more features
3. **Scale**: 1,000,000 users, enterprise features

**Requirements**:
1. For each stage:
   - Describe the architecture
   - List key components
   - Estimate costs
   - Identify limitations

2. Plan the evolution:
   - What changes between stages?
   - What stays the same?
   - How to migrate between stages?

**Deliverables**:
- `exercise5_1_evolution_plan.md`
- Architecture diagrams for each stage
- Migration plan
- Cost/scale estimates

**Learning Goals**:
- Evolution planning
- Scalability thinking
- Migration planning

---

### Exercise 5.2: Refactor for Evolution 🟡

**Objective**: Practice refactoring to enable future evolution.

**Task**:
You have a monolithic application that needs to evolve. Refactor it to support:

1. Multiple deployment environments (dev, staging, prod)
2. Feature flags (enable/disable features)
3. Plugin system (add features without modifying core)
4. Horizontal scaling (run multiple instances)

**Requirements**:
1. Start with a simple monolithic app
2. Refactor to support each evolution requirement
3. Show how each change enables evolution
4. Document the refactoring process

**Deliverables**:
- `exercise5_2_evolution_refactor.py`
- Refactoring documentation
- Before/after comparison
- Evolution capabilities demonstration

**Learning Goals**:
- Evolution-enabling refactoring
- Future-proofing design
- Incremental improvement

---

### Exercise 5.3: Design for Change 🔴

**Objective**: Design a system that can evolve easily.

**Task**:
Design a content management system (CMS) that can:

1. Support multiple content types (blog posts, videos, products, etc.)
2. Add new content types without code changes
3. Support multiple frontends (web, mobile, API)
4. Scale from small to large deployments
5. Support multiple tenants (multi-tenancy)

**Requirements**:
1. Design the architecture with evolution in mind
2. Use patterns that enable change:
   - Plugin architecture
   - Strategy pattern
   - Adapter pattern
   - Configuration over code

3. Show how new features can be added
4. Demonstrate scalability paths

**Deliverables**:
- `exercise5_3_evolution_design.py`
- Architecture design document
- Evolution scenarios
- Code examples

**Learning Goals**:
- Evolution-first design
- Change-enabling patterns
- Future-proofing

---

## COMPREHENSIVE EXERCISES

### Exercise 6.1: Complete System Design 🟡

**Objective**: Apply all concepts from Lecture 1 in one project.

**Task**:
Design and implement a complete system (e.g., task management, social network, marketplace) that demonstrates:

1. **Abstraction**: Use interfaces for key components
2. **Modularity**: Separate into independent components
3. **Communication**: Document architecture with multiple views
4. **Quality Attributes**: Make explicit trade-off decisions
5. **Evolution**: Design for future growth

**Requirements**:
1. Implement a working system (can be simplified)
2. Use all architectural principles
3. Create comprehensive documentation
4. Explain design decisions
5. Show evolution path

**Deliverables**:
- Complete codebase
- Architecture documentation
- Design rationale
- Evolution plan

**Learning Goals**:
- Integration of all concepts
- Complete system design
- Practical application

---

### Exercise 6.2: Architecture Review 🔴

**Objective**: Practice evaluating and improving architectures.

**Task**:
Take an existing system (open source or your own) and:

1. **Analyze**: Identify architectural patterns, quality attributes, trade-offs
2. **Evaluate**: Assess strengths and weaknesses
3. **Improve**: Propose architectural improvements
4. **Refactor**: Implement key improvements
5. **Document**: Create architecture documentation

**Requirements**:
1. Choose a system with some complexity
2. Perform thorough analysis
3. Propose concrete improvements
4. Implement at least 2-3 improvements
5. Document the process

**Deliverables**:
- Analysis document
- Improvement proposals
- Refactored code
- Architecture documentation

**Learning Goals**:
- Critical evaluation
- Improvement skills
- Refactoring practice

---

## EXERCISE SUBMISSION GUIDELINES

### For Each Exercise:

1. **Code**: Well-commented, following best practices
2. **Documentation**: Clear explanations and diagrams
3. **Tests**: Unit tests for key components (where applicable)
4. **Reflection**: Brief explanation of what you learned

### File Naming:
- `exercise{set}_{number}_{name}.py` for code
- `exercise{set}_{number}_{name}.md` for documentation

### Example:
- `exercise1_1_storage_abstraction.py`
- `exercise1_1_storage_abstraction.md`

---

## RECOMMENDED EXERCISE PROGRESSION

### Week 1: Foundations
- Exercise 1.1 (Abstraction)
- Exercise 2.1 (Modularity)
- Exercise 3.1 (Communication)

### Week 2: Application
- Exercise 1.2 (Refactoring)
- Exercise 2.2 (System Design)
- Exercise 4.1 (Quality Attributes)

### Week 3: Advanced
- Exercise 1.3 (Plugin System)
- Exercise 4.2 (Trade-offs)
- Exercise 5.1 (Evolution Planning)

### Week 4: Integration
- Exercise 6.1 (Complete System)
- Exercise 6.2 (Architecture Review)

---

## TIPS FOR SUCCESS

1. **Start Simple**: Begin with beginner exercises to build confidence
2. **Compare**: Always compare your solutions to the example code
3. **Reflect**: After each exercise, think about what you learned
4. **Experiment**: Try variations and see what happens
5. **Document**: Good documentation is as important as good code
6. **Review**: Look at bad examples to understand what to avoid

---

## ADDITIONAL RESOURCES

- Review `TUTORIAL.md` for detailed explanations
- Study the example files in this directory
- Learn from `bad_examples/` to avoid common mistakes
- Use `TUTORIAL.html` for interactive learning

---

## GETTING HELP

If you're stuck:
1. Review the example files
2. Check the tutorial materials
3. Look at bad examples to understand problems
4. Start with simpler exercises
5. Break problems into smaller parts

Good luck with your exercises! 🚀


