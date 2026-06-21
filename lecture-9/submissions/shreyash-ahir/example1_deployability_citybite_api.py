#!/usr/bin/env python3
"""
Example 1: Deployability — CityBite (food delivery) API configuration

Real-world scenario
-------------------
CityBite runs a **Python order API** behind nginx on laptops (dev), EC2 (legacy),
and later **AWS ECS Fargate**. Ops injects environment variables; Kubernetes
sets PORT; secrets never live in the image.

This script does NOT start a web server. It shows how **twelve-factor style**
configuration makes the *same* codebase deployable across environments, and
how **anti-patterns** break production.

Reference: Chapter 9 — Deployability, Portability, and Containers (Pautasso)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class AntiPatternConfig:
    """
    How the API was wired when a single developer shipped from their laptop:
    breaks in Linux containers (wrong path, fixed port, DB on C: drive).
    """

    database_path: str = r"C:\CityBite\data\orders.sqlite"
    listen_port: int = 5000
    log_file: str = r"C:\CityBite\logs\api.log"


@dataclass(frozen=True)
class PortableConfig:
    """
    What SRE expects in ECS/Kubernetes: config from the environment,
    logs on stdout (for CloudWatch / Loki), bind PORT from platform.
    """

    database_url: str
    listen_port: int
    log_level: str
    aws_region: str

    @classmethod
    def from_env(cls) -> "PortableConfig":
        port_raw = os.environ.get("PORT", "8080")
        try:
            port = int(port_raw)
        except ValueError:
            port = 8080
        return cls(
            database_url=os.environ.get(
                "DATABASE_URL",
                "sqlite:///./citybite_orders_dev.sqlite",
            ),
            listen_port=port,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            aws_region=os.environ.get("AWS_REGION", "eu-central-1"),
        )


def log_json(portable: PortableConfig, event: str, extra: Dict[str, Any]) -> None:
    """Structured log line → stdout (container-friendly)."""
    line = {
        "service": "citybite-order-api",
        "event": event,
        "log_level": portable.log_level,
        "region": portable.aws_region,
        **extra,
    }
    print(json.dumps(line, sort_keys=True))


def main() -> None:
    print("=" * 64)
    print("Example 1: Deployability — CityBite order API")
    print("=" * 64)

    print("\n--- Anti-pattern (do not ship like this) ---")
    bad = AntiPatternConfig()
    print(f"  database_path = {bad.database_path!r}")
    print(f"  listen_port   = {bad.listen_port}")
    print(f"  log_file      = {bad.log_file!r}")
    print("  → Fails on Linux containers: no C:\\ drive; port 5000 may conflict;")
    print("    log file path is not writable under read-only root FS.")

    print("\n--- Portable config (from environment) ---")
    # Simulate production-like env without touching user's filesystem
    os.environ.setdefault("PORT", "8080")
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://citybite:***@orders-db.citybite.internal:5432/orders",
    )
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("AWS_REGION", "eu-central-1")

    good = PortableConfig.from_env()
    db_disp = good.database_url if len(good.database_url) <= 60 else good.database_url[:57] + "..."
    print(f"  DATABASE_URL  = {db_disp}")
    print(f"  PORT          = {good.listen_port}")
    print(f"  LOG_LEVEL     = {good.log_level}")
    print(f"  AWS_REGION    = {good.aws_region}")
    log_json(
        good,
        "config_loaded",
        {"listen_port": good.listen_port, "db_scheme": good.database_url.split(":", 1)[0]},
    )

    print("\n--- Why this matters for deployability ---")
    print("  • Fargate/Kubernetes sets PORT; binding to it avoids port clashes.")
    print("  • DATABASE_URL switches dev SQLite vs managed Postgres without code edits.")
    print("  • JSON logs on stdout ship to your log aggregator without mounting volumes.")
    print("=" * 64)


if __name__ == "__main__":
    main()
