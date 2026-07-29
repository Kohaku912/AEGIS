#!/usr/bin/env python3
"""Run autonomous goal hygiene inside the AI Server container or host venv.

Usage:
  python -m aegis_ai.agency.sweep_cli --dry-run
  python -m aegis_ai.agency.sweep_cli --apply
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sweep polluted autonomous goals")
    parser.add_argument("--apply", action="store_true", help="Apply cancellations (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Report only (default)")
    args = parser.parse_args(argv)
    dry_run = not args.apply

    from aegis_ai.agency.goal_hygiene import sweep_pollution
    from aegis_ai.runtime import get_runtime

    runtime = get_runtime()
    stats = sweep_pollution(
        task_manager=getattr(runtime, "task_manager", None),
        continuation_manager=getattr(runtime, "continuation_manager", None),
        repair_manager=getattr(runtime, "repair_manager", None),
        dry_run=dry_run,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
