#!/usr/bin/env python3
"""
Example 2: Portability — CityBite restaurant menu images

Real-world scenario
-------------------
Restaurants upload **menu photos**. In development, engineers save files under
`./uploads`. In **Docker**, the container image filesystem is often ephemeral or
read-only except mounted volumes — writing to `./uploads` fails at runtime.

This example compares a **non-portable** path (cwd-relative) with a portable
path driven by **DATA_DIR** (e.g. mounted `emptyDir` or EFS in EKS).

Reference: Chapter 9 — Deployability, Portability, and Containers (Pautasso)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def bad_save_path(filename: str) -> Path:
    """Assumes current working directory is writable — often false in K8s."""
    return Path("uploads") / "menus" / filename


def portable_save_path(filename: str) -> Path:
    """
    Use DATA_DIR from environment (set by Helm to /var/data or /tmp/probes).
    Falls back to OS temp directory for local runs.
    """
    base = os.environ.get("DATA_DIR", tempfile.gettempdir())
    root = Path(base) / "citybite" / "menu-uploads"
    return root / filename


def simulate_write(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake-jpeg-bytes")
    return str(path.resolve())


def main() -> None:
    print("=" * 64)
    print("Example 2: Portability — CityBite menu uploads")
    print("=" * 64)

    fname = "restaurant-4421-hero.jpg"

    print("\n--- Non-portable: relative to cwd ---")
    p_bad = bad_save_path(fname)
    print(f"  Target: {p_bad}")
    print("  Risk: in a minimal container, cwd may be read-only or wiped on restart.")

    print("\n--- Portable: DATA_DIR + stable layout ---")
    if "DATA_DIR" not in os.environ:
        os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="citybite_data_")
    p_good = portable_save_path(fname)
    written = simulate_write(p_good)
    print(f"  DATA_DIR = {os.environ['DATA_DIR']}")
    print(f"  Wrote     = {written}")

    print("\n--- Ops checklist (real clusters) ---")
    print("  • Mount a volume or use object storage (S3) for durable binaries.")
    print("  • Never bake customer uploads into the image — breaks immutability.")
    print("  • Use the same path convention in dev (docker-compose volume) and prod.")
    print("=" * 64)


if __name__ == "__main__":
    main()
