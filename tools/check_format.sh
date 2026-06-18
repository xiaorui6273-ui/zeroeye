#!/usr/bin/env bash
# check_format.sh — Verify all source files match .editorconfig settings
# Exits non-zero if any file violates its language's formatting rules.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EDITORCONFIG="$ROOT/.editorconfig"
ERRORS=0

# Check if .editorconfig exists
if [ ! -f "$EDITORCONFIG" ]; then
    echo "ERROR: .editorconfig not found at $EDITORCONFIG"
    exit 1
fi

echo "Checking formatting against .editorconfig..."

# Check Rust files: 4-space indent, no tabs
echo "  Checking Rust files (4-space indent)..."
while IFS= read -r -d '' file; do
    if grep -qP '\t' "$file"; then
        echo "    VIOLATION: $file contains tabs (expected 4-space indent)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" -name "*.rs" -not -path "*/target/*" -not -path "*/.git/*" -print0)

# Check Go files: tabs expected
echo "  Checking Go files (tabs)..."
while IFS= read -r -d '' file; do
    if ! grep -qP '\t' "$file"; then
        # Allow files that are all spaces if they're very small
        lines=$(wc -l < "$file")
        if [ "$lines" -gt 5 ]; then
            echo "    VIOLATION: $file has no tabs (expected tab indent)"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done < <(find "$ROOT" -name "*.go" -not -path "*/.git/*" -print0)

# Check Python files: 4-space indent, no tabs
echo "  Checking Python files (4-space indent)..."
while IFS= read -r -d '' file; do
    if grep -qP '^\t' "$file"; then
        echo "    VIOLATION: $file starts lines with tabs (expected 4-space indent)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" -name "*.py" -not -path "*/.git/*" -print0)

# Check TypeScript files: 2-space indent, no tabs
echo "  Checking TypeScript files (2-space indent)..."
while IFS= read -r -d '' file; do
    if grep -qP '^\t' "$file"; then
        echo "    VIOLATION: $file starts lines with tabs (expected 2-space indent)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" -name "*.ts" -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/.git/*" -print0)

# Check shell scripts: 2-space indent
echo "  Checking shell scripts (2-space indent)..."
while IFS= read -r -d '' file; do
    if grep -qP '^\t' "$file"; then
        echo "    VIOLATION: $file starts lines with tabs (expected 2-space indent)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" -name "*.sh" -not -path "*/.git/*" -print0)

# Check C files: 4-space indent (matching existing codebase)
echo "  Checking C files (4-space indent)..."
while IFS= read -r -d '' file; do
    if grep -qP '^\t' "$file"; then
        echo "    VIOLATION: $file starts lines with tabs (expected 4-space indent)"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" -name "*.c" -not -path "*/.git/*" -print0)

# Check final newlines
echo "  Checking final newlines..."
while IFS= read -r -d '' file; do
    if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -l)" -eq 0 ]; then
        echo "    VIOLATION: $file missing final newline"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$ROOT" \( -name "*.rs" -o -name "*.go" -o -name "*.ts" -o -name "*.py" -o -name "*.c" -o -name "*.h" -o -name "*.java" -o -name "*.rb" -o -name "*.lua" -o -name "*.hs" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/target/*" -not -path "*/dist/*" -not -path "*/diagnostic/*" -print0)

echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "FORMAT CHECK FAILED: $ERRORS violation(s) found"
    exit 1
else
    echo "FORMAT CHECK PASSED: All files match .editorconfig"
    exit 0
fi
