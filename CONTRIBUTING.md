# Contributing to Tent of Trials

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

### Prerequisites

- **Python 3.10+** — for build tooling and backend
- **Rust** (latest stable) — for backend services
- **Node.js 22+** — for frontend
- **Go** — for market engine

### Clone and Setup

```bash
git clone https://github.com/lobster-trap/zeroeye
cd zeroeye

# Install Python dependencies
python3 -m pip install -r requirements.txt  # if present

# Install Rust dependencies
source "$HOME/.cargo/env"
cargo fetch

# Install Node.js dependencies
npm install
```

### Build

Run the diagnostic build pipeline:

```bash
python3 build.py
```

This generates build diagnostics in the `diagnostic/` directory. Include the generated `.logd` and `.json` artifacts in your PR notes.

## PR Workflow

1. **Fork** the repository
2. **Create a branch** from `main`: `git checkout -b my-feature`
3. **Commit** your changes with clear messages
4. **Push** to your fork
5. **Open a Pull Request** against `lobster-trap/zeroeye:main`

### PR Requirements

- Use the pull request template (`.github/pull_request_template.md`)
- Include diagnostic build artifacts from `python3 build.py` in PR notes
- Keep changes scoped to the PR purpose
- No unrelated cleanup or formatting changes
- All tests must pass locally

## Code Style

This project uses [`.editorconfig`](.editorconfig) for consistent formatting. Please ensure your editor supports it.

| Language | Indent | Size |
|----------|--------|------|
| Python | spaces | 4 |
| Rust | spaces | 4 |
| TypeScript/JavaScript | spaces | 2 |
| Go | tabs | 4 |
| C/C++ | tabs | 4 |
| Ruby | spaces | 2 |
| Shell | spaces | 4 |
| YAML/JSON/Markdown | spaces | 2 |
| Makefile | tabs | — |

## Questions?

Open an issue for discussion before starting significant work.
