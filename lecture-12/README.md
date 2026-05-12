# Lecture 12: Flexibility and Microservices

## Overview

Materials for **Chapter 12: Flexibility and Microservices** (Pautasso).

Focus: **modifiability / flexibility**; **monolith vs modular monolith vs microservices**; **bounded contexts** and **Conway’s Law**; **database per service**; **API evolution**; **sagas** (intro); migration patterns (**strangler fig**, **branch by abstraction**); pitfalls (**distributed monolith**, chatty services).

**Chapter PDF:** `12_Flexibility_and_Microservices.pdf` — place a copy in this folder or use `../chapters/12_Flexibility_and_Microservices.pdf` if your layout matches the repo root.

## Learning Objectives

1. **Flexibility** — Modifiability, drivers of change, coupling vs cohesion  
2. **Monolith & modular monolith** — When to stay coarse-grained; internal seams  
3. **Microservices** — Autonomous deployment, decentralized data, operational implications  
4. **Boundaries** — Bounded contexts, database per service, API contracts  
5. **Migration** — Strangler fig, branch by abstraction, dual-write caution  
6. **Distributed design** — Sagas, eventual consistency, choreography vs orchestration (high level)

## Example Files (CityBite)

### `example1_flexibility_coupling_citybite.py`

**Scenario:** `OrderService` depends on payment code.

- **Anti-pattern:** import concrete payment implementation — blocks extraction  
- **Pattern:** **port** (protocol) + **adapter** — same process today, microservice tomorrow

### `example2_flexibility_api_evolution_citybite.py`

**Scenario:** public **Orders** JSON API.

- **Additive** vs **breaking** changes — ties to **backward compatibility** and deprecation policy

## Running the Examples

```bash
cd arch-course-cu/lecture-12
python3 example1_flexibility_coupling_citybite.py
python3 example2_flexibility_api_evolution_citybite.py
```

## Lecture presentation

- **`LECTURE_SLIDES_MARP.md`** — Primary deck; **What / Why** bullets for read-aloud. Each slide ends with a **`Definitions`** block (blockquote) glossing bolded terms on that slide.  
- **`Lecture12.pptx`** / **`LECTURE_SLIDES_marp.html`** — export from Marp:

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture12.pptx
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o LECTURE_SLIDES_marp.html --html
  ```

## Assignment

See **`ASSIGNMENT.md`** — CityBite **bounded contexts**, **strangler** migration, **API evolution**, **Conway** reflection, **saga** sketch, and **diagram** (**documentation + diagrams**).

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Lecture 11:** Availability & Services  
- **Lecture 10:** Scalability  

## Next Steps

- Draw **three** bounded contexts for CityBite — mark **events** that cross boundaries  
- List **one** change that must stay **ACID** in-process vs **one** that can be **eventual**
