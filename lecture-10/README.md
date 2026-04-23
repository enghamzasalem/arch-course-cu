# Lecture 10: Scalability

## Overview

Materials for **Chapter 10: Scalability** (Pautasso).

Focus: growing **workloads** (CityBite dinner rush, marketing pushes) vs **resources**; **scale up** vs **scale out**; bottlenecks in the hot path; **state**, **caching**, **queues**, **sharding**, and classic **patterns** (load balance, scatter/gather, master/worker).

**Chapter PDF:** place `10_Scalability.pdf` in this folder (or use the copy under `../chapters/`).

**Lecture transcript (optional):** `lectrue10.txt` — aligns slides with spoken chapter notes; used when expanding the deck.

## Learning Objectives

1. **Scalability** — Define in terms of workload dimensions and resource limits
2. **Scale up vs scale out** — When vertical growth stops; economics of replicas
3. **Bottlenecks** — CPU, memory, disk, network, locks, single-writer databases
4. **State** — What must stay consistent vs what can be partitioned or cached
5. **Patterns** — Load balancing, partitions/shards, caches, async workers, scatter/gather
6. **Measurement** — Saturation, latency percentiles, and capacity tests tied to architecture

## Example Files (real-world scenarios)

### `example1_scalability_hot_path_citybite.py`

**Scenario:** **CityBite** kitchen dashboard — **active orders for one restaurant**.

- **Anti-pattern:** one global list scanned for every query → cost grows with **all** restaurants’ orders
- **Better:** partition / index by `restaurant_id` → work scoped to the tenant that matters

### `example2_scalability_queue_workers_citybite.py`

**Scenario:** **CityBite** post-checkout **push/email notifications**.

- **Anti-pattern:** synchronous outbound calls inside the checkout request
- **Better:** **enqueue** and process with a **worker pool** (models parallel consumers and decoupled throughput)

## Running the Examples

```bash
cd arch-course-cu/lecture-10
python3 example1_scalability_hot_path_citybite.py
python3 example2_scalability_queue_workers_citybite.py
```

## Lecture presentation

- **`LECTURE_SLIDES_MARP.md`** — Primary slide source. Bullets are written for **read-aloud**: each line uses **What:** (definition / mechanism) and **Why:** (motivation / consequence) so you can present **without** hidden speaker notes.
- **`Lecture10.pptx`** — Export from Marp (same content as the markdown).

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture10.pptx
  ```

- **`LECTURE_SLIDES_marp.html`** — Same deck as a single **HTML** page (open in browser; print to PDF if needed):

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o LECTURE_SLIDES_marp.html --html
  ```

- **`LECTURE_PRESENTATION.html`** — Dark **cursor** deck (keyboard navigation). Content is a **shorter** companion; use **PPTX** or **`LECTURE_SLIDES_marp.html`** when you want the full **What / Why** presenter script on every slide.

## Assignment

See **`ASSIGNMENT.md`**. You document how **CityBite** scales for **peak demand** (data + compute + operations), aligned with the examples and Chapter 10.

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Lecture 9:** Deployability, Portability, and Containers  
- **Lecture 11 (course arc):** Availability, flexibility — deeper runtime qualities (per textbook ordering)

## Next Steps

- Pick **one** dominant workload story (e.g. order placement vs search) and quantify limits
- Run a **cheap** load experiment on paper: “what breaks first at 10× traffic?”
