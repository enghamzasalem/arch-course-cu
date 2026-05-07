# Lecture 11: Availability and Services

## Overview

Materials for **Chapter 11: Availability and Services** (Pautasso).

Focus: **components vs services** (ownership, remote connectors, SaaS); **operational availability**; **monitoring** (active/passive, probes); **downtime** cost; **cascading failures**, **circuit breaker**, **canary call**; **replication** and the **consistency vs availability** tension; **event sourcing** (high level).

**Chapter PDF:** `11_Availability_and_Services.pdf` (also under `../chapters/`).

**Lecture transcript (optional):** `lect11.txt` — note: if the file opens as “binary” in some editors, it may contain NUL bytes; `tr -d '\000' < lect11.txt` prints clean text.

## Learning Objectives

1. **Components vs services** — Who operates the software; remote connectors; trust boundaries  
2. **Availability** — Uptime, MTBF/MTTR intuition, SLIs/SLOs as contracts  
3. **Monitoring** — Watchdog vs monitor; liveness vs readiness style thinking  
4. **Cascading failure** — Retries, timeouts, **circuit breaker**, **canary** requests  
5. **Replication** — Sync vs async; availability vs consistency trade-offs (CAP preview)  
6. **Event sourcing** — Append-only facts for audit/replay (when it helps availability stories)

## Example Files (CityBite)

### `example1_availability_circuit_breaker_citybite.py`

**Scenario:** checkout → **payment gateway** flaps or slows down.

- **Anti-pattern:** tight retry loop hammers a sick dependency  
- **Pattern:** **circuit breaker** — fail fast / cooldown — limits blast radius

### `example2_availability_monitoring_citybite.py`

**Scenario:** **readiness** vs trivial **health** when the **DB pool** is exhausted.

- **What:** shallow “process OK” vs **deep** “can we still take orders?”  
- **Why:** aligns with Kubernetes probes and **meaningful** SLIs

## Running the Examples

```bash
cd arch-course-cu/lecture-11
python3 example1_availability_circuit_breaker_citybite.py
python3 example2_availability_monitoring_citybite.py
```

## Lecture presentation

- **`LECTURE_SLIDES_MARP.md`** — Primary deck; **What / Why** bullets for read-aloud. Each slide ends with a **`Definitions`** block (blockquote) glossing bolded terms on that slide.  
- **`Lecture11.pptx`** / **`LECTURE_SLIDES_marp.html`** — export from Marp:

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture11.pptx
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o LECTURE_SLIDES_marp.html --html
  ```

- **`LECTURE_PRESENTATION.html`** — Short dark companion deck (keyboard nav). Full script: **PPTX** or **`LECTURE_SLIDES_marp.html`**.

## Assignment

See **`ASSIGNMENT.md`** — CityBite **SLOs**, monitoring, failure containment, and replication (**documentation + diagrams**).

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Lecture 10:** Scalability  
- **Lecture 12 (course arc):** Flexibility and Microservices  

## Next Steps

- Pick **one** external SaaS CityBite depends on — write its **failure modes** and your **fallback**
- Define **one** SLO with a measurable **SLI** (e.g. successful checkout ratio)
