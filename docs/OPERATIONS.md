# Operations Guide

## Build Diagnostics

### Running the build

```bash
python3 build.py
```

This generates encrypted diagnostic artifacts in `diagnostic/`:
- `diagnostic/build-{commit}.logd` — encrypted build log
- `diagnostic/build-{commit}.json` — metadata including module statuses, durations, and artifact paths

### Comparing diagnostic builds

Use the diagnostic diff tool to compare two build results:

```bash
python3 tools/diagnostic_diff.py diagnostic/build-abc123.json diagnostic/build-def456.json
```

For machine-readable output:

```bash
python3 tools/diagnostic_diff.py --json diagnostic/build-abc123.json diagnostic/build-def456.json
```

### Checking code formatting

```bash
bash tools/check_format.sh
```

Verifies all source files match the `.editorconfig` conventions. Exits non-zero if violations are found.
