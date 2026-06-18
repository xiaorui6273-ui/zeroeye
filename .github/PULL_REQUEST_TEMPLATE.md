## Summary

Adds `.editorconfig` to codify existing formatting conventions across the polyglot codebase, plus a `tools/check_format.sh` script to enforce them.

## Changes

- `.editorconfig` — covers all languages in the repo:
  - Rust: 4-space indent
  - Go: tabs
  - Python: 4-space indent
  - C: 4-space indent (matches existing codebase)
  - TypeScript/JavaScript: 2-space indent
  - Shell: 2-space indent (matches existing codebase)
  - Ruby: 2-space indent
  - Lua: 2-space indent
  - Haskell: 2-space indent
  - Java: 4-space indent
  - JSON/YAML: 2-space indent
- `tools/check_format.sh` — verifies all files match .editorconfig, exits non-zero on violations
- `docs/OPERATIONS.md` — documents build diagnostics and format checking

## Testing

```bash
bash tools/check_format.sh
# FORMAT CHECK PASSED: All files match .editorconfig
```

Zero violations across all source files.

## Checklist

- [x] .editorconfig covers all languages in the repo
- [x] Settings match existing conventions (don't reformat, just codify)
- [x] check_format.sh verifies all files and exits non-zero on violations
- [x] check_format.sh passes on current codebase (0 violations)
- [x] Usage documented in docs/OPERATIONS.md
- [x] Diagnostic build log committed

Closes #58
