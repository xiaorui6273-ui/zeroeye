#!/usr/bin/env python3
"""
test_determinism.py — Validate that data_generator.py produces
byte-for-byte identical output for the same seed.

Usage:
    python3 tools/test_determinism.py
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_GENERATOR = REPO_ROOT / "tools" / "data_generator.py"
SEEDS = [42, 12345, 999999]
ITERATIONS = 3


def run_generator(seed: int, output_dir: str) -> dict:
    """Run data_generator.py and return file hashes."""
    result = subprocess.run(
        [sys.executable, str(DATA_GENERATOR),
         "--seed", str(seed),
         "--output-dir", output_dir,
         "--users", "10",
         "--orders", "20",
         "--trades", "30",
         "--ticks", "50",
         "--candles", "20",
         "--format", "json"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        print(f"  FAILED (seed={seed}): {result.stderr}")
        return {}

    hashes = {}
    for f in Path(output_dir).glob("*.json"):
        content = f.read_bytes()
        hashes[f.name] = hashlib.sha256(content).hexdigest()
    return hashes


def main() -> int:
    print("Testing data_generator.py determinism...\n")
    all_passed = True

    for seed in SEEDS:
        print(f"  Seed {seed}:")
        reference_hashes = None

        for i in range(ITERATIONS):
            tmpdir = tempfile.mkdtemp(prefix=f"dg_test_{seed}_{i}_")
            try:
                hashes = run_generator(seed, tmpdir)
                if not hashes:
                    all_passed = False
                    continue

                if reference_hashes is None:
                    reference_hashes = hashes
                    print(f"    Iteration {i+1}: OK (reference)")
                else:
                    if hashes == reference_hashes:
                        print(f"    Iteration {i+1}: OK (identical)")
                    else:
                        print(f"    Iteration {i+1}: FAIL (mismatch!)")
                        for fname in sorted(set(hashes) | set(reference_hashes)):
                            h1 = reference_hashes.get(fname, "<missing>")
                            h2 = hashes.get(fname, "<missing>")
                            if h1 != h2:
                                print(f"      {fname}: {h1[:12]}... != {h2[:12]}...")
                        all_passed = False
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

    print()
    if all_passed:
        print(f"ALL PASSED: {len(SEEDS)} seeds × {ITERATIONS} iterations")
        return 0
    else:
        print("SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
