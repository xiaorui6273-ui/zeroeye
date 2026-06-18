# Test Data

This directory contains generated test data for development and testing.

## Usage

Generate with a specific seed (deterministic):

```bash
python3 tools/data_generator.py --seed 42 --output-dir ./test_data
```

Generate with a random seed (prints seed for reproducibility):

```bash
python3 tools/data_generator.py --output-dir ./test_data
# Output: Generating test data with seed 12345678...
```

Print only the seed that would be used:

```bash
python3 tools/data_generator.py --print-seed
# Output: Seed: 98765432
```

## Deterministic Output

When the same seed and arguments are provided, output is byte-for-byte identical:

```bash
# Run 1
python3 tools/data_generator.py --seed 42 --users 10 --orders 20
# Run 2 (identical output)
python3 tools/data_generator.py --seed 42 --users 10 --orders 20
```

## Output Format

JSON files include a `_meta` header with the seed and timestamp:

```json
{
  "_meta": {
    "generator": "data_generator.py",
    "seed": 42,
    "generated_at": "2026-01-15T12:00:00+00:00"
  },
  "data": [...]
}
```

## Verification

Run the determinism test:

```bash
python3 tools/test_determinism.py
```

This validates 3 different seeds across 3 iterations each.
