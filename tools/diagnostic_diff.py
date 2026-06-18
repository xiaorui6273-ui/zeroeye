#!/usr/bin/env python3
"""
diagnostic_diff.py — Compare two diagnostic metadata JSON files.

Usage:
    python3 tools/diagnostic_diff.py <path1> <path2>
    python3 tools/diagnostic_diff.py <path1> <path2> --json

Exits non-zero when either input file is missing or contains invalid JSON.
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


def load_json(path: str) -> Dict[str, Any]:
    """Load a JSON file, exiting on error."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def diff_diagnostics(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two diagnostic metadata dicts and return a structured diff."""
    old_modules: Dict[str, Dict[str, Any]] = {
        m["name"]: m for m in old.get("modules", [])
    }
    new_modules: Dict[str, Dict[str, Any]] = {
        m["name"]: m for m in new.get("modules", [])
    }

    old_names: set = set(old_modules.keys())
    new_names: set = set(new_modules.keys())

    added: List[str] = sorted(new_names - old_names)
    removed: List[str] = sorted(old_names - new_names)
    common: List[str] = sorted(old_names & new_names)

    changed_status: List[Dict[str, Any]] = []
    duration_deltas: List[Dict[str, Any]] = []

    for name in common:
        om = old_modules[name]
        nm = new_modules[name]

        if om.get("status") != nm.get("status"):
            changed_status.append({
                "module": name,
                "old_status": om.get("status"),
                "new_status": nm.get("status"),
            })

        old_elapsed = om.get("elapsed_seconds", 0) or 0
        new_elapsed = nm.get("elapsed_seconds", 0) or 0
        delta = new_elapsed - old_elapsed
        if abs(delta) > 0.001:
            duration_deltas.append({
                "module": name,
                "old_seconds": old_elapsed,
                "new_seconds": new_elapsed,
                "delta_seconds": round(delta, 3),
            })

    return {
        "added_modules": added,
        "removed_modules": removed,
        "changed_status": changed_status,
        "duration_deltas": duration_deltas,
        "old_total_passed": old.get("passed", 0),
        "new_total_passed": new.get("passed", 0),
        "old_total_failed": old.get("failed", 0),
        "new_total_failed": new.get("failed", 0),
    }


def format_text(diff: Dict[str, Any]) -> str:
    """Format diff dict as human-readable text."""
    lines: List[str] = []

    added = diff["added_modules"]
    if added:
        lines.append(f"Added modules ({len(added)}):")
        for name in added:
            lines.append(f"  + {name}")

    removed = diff["removed_modules"]
    if removed:
        lines.append(f"Removed modules ({len(removed)}):")
        for name in removed:
            lines.append(f"  - {name}")

    changed = diff["changed_status"]
    if changed:
        lines.append(f"Changed status ({len(changed)}):")
        for c in changed:
            lines.append(
                f"  ~ {c['module']}: {c['old_status']} -> {c['new_status']}"
            )

    deltas = diff["duration_deltas"]
    if deltas:
        lines.append(f"Duration changes ({len(deltas)}):")
        for d in deltas:
            sign = "+" if d["delta_seconds"] >= 0 else ""
            lines.append(
                f"  {d['module']}: {d['old_seconds']}s -> {d['new_seconds']}s "
                f"({sign}{d['delta_seconds']}s)"
            )

    # Summary
    old_pass = diff["old_total_passed"]
    new_pass = diff["new_total_passed"]
    old_fail = diff["old_total_failed"]
    new_fail = diff["new_total_failed"]
    lines.append(
        f"Summary: passed {old_pass} -> {new_pass}, failed {old_fail} -> {new_fail}"
    )

    if not (added or removed or changed or deltas):
        lines.append("No differences found.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two diagnostic metadata JSON files"
    )
    parser.add_argument("path1", help="Path to the first (older) diagnostic JSON")
    parser.add_argument("path2", help="Path to the second (newer) diagnostic JSON")
    parser.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON diff"
    )
    args = parser.parse_args()

    old = load_json(args.path1)
    new = load_json(args.path2)

    diff = diff_diagnostics(old, new)

    if args.json:
        print(json.dumps(diff, indent=2))
    else:
        print(format_text(diff))

    return 0


if __name__ == "__main__":
    sys.exit(main())
