# Pre-commit Hook

The pre-commit hook automatically runs `python3 build.py` before every commit
and stages the generated diagnostic artifacts.

## Installation

```bash
make install-hooks
```

This symlinks `tools/pre-commit` into `.git/hooks/pre-commit`.

## What it does

1. Runs `python3 build.py` with a countdown timer
2. If the build fails, the commit is aborted with a clear error message
3. If the build succeeds, the latest diagnostic artifacts (`.logd` and `.json`)
   are automatically staged
4. If diagnostics haven't changed since last commit, the rebuild is skipped
   (using file hash comparison)

## Requirements

- Python 3.10+
- Must be run from the repository root

## Bypass

To skip the hook for a specific commit:

```bash
git commit --no-verify
```
