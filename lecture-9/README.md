# Lecture 9: Deployability, Portability, and Containers

## Overview

Materials for **Chapter 9: Deployability, Portability, and Containers** (Pautasso).

Focus: shipping software **reliably** and **often**; running the same artifact in **dev, staging, and prod**; **containers** as the unit of packaging and scheduling; operational concerns (config, logs, health, storage).

**Chapter PDF:** place `09_Deployability_Portability_and_Containers.pdf` in this folder (or use the copy under `../chapters/`).

## Learning Objectives

1. **Deployability** — Frequency, automation, rollback, environment parity
2. **Portability** — Host independence, paths, configuration, dependencies
3. **Containers** — Images, layers, immutability, isolation (conceptual)
4. **Processes** — One main process, signals, disposability
5. **Configuration** — Environment, secrets, twelve-factor style practices
6. **Operations** — Health checks, logs, resources, stateful vs stateless data

## Example Files (real-world scenarios)

### `example1_deployability_citybite_api.py`

**Scenario:** **CityBite** — a regional food-delivery company’s **order API** moving from developer laptops → EC2 → **AWS ECS**.

- Contrasts **anti-patterns** (hardcoded Windows paths, local log files) with **portable** config (`PORT`, `DATABASE_URL`, `LOG_LEVEL`, region)
- Shows **structured logs on stdout** for log aggregation in the cloud

### `example2_portability_menu_uploads.py`

**Scenario:** **CityBite** — restaurants upload **menu photos**.

- Shows why `./uploads` breaks under typical **container** filesystem rules
- Uses **`DATA_DIR`** (volume / temp) for a portable path layout

## Running the Examples

```bash
cd arch-course-cu/lecture-9
python3 example1_deployability_citybite_api.py
python3 example2_portability_menu_uploads.py
```

## Lecture presentation

- **`LECTURE_PRESENTATION.html`** — Browser deck: **F** fullscreen, **P** print / Save as PDF.
- **`LECTURE_SLIDES_MARP.md`** — Marp → PowerPoint:

  ```bash
  npx @marp-team/marp-cli --no-stdin LECTURE_SLIDES_MARP.md -o Lecture9.pptx
  ```

## Assignment

See **`ASSIGNMENT.md`**. You design how **CityBite** (same product as the examples) runs on **Kubernetes** after a lift from VMs — deployability, container images, portability, and a rollout story (documentation + diagrams; no full cluster required).

Submission: GitHub Pull Request (see `../lecture-3/SUBMISSION_GUIDE.md`).

## Related Materials

- **Lecture 7:** Composability and Connectors  
- **Lecture 8:** Compatibility and Coupling  
- **Lecture 6:** Interfaces and reuse (config surfaces as contracts)

## Next Steps

- **Lecture 10 (Chapter 10 — Scalability):** `../lecture-10/`
- Map each runtime concern to an owner (app vs platform vs SRE)
- Prefer immutable artifacts and explicit config boundaries
