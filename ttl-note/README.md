# ttl-note

Time-To-Live code annotations. TODO comments with teeth.

Codebases accumulate `// TODO` and `// HACK` comments that never get cleaned up.
`ttl-note` attaches **expiration conditions** to code annotations and surfaces
the expired ones as actionable warnings. It's a dead man's switch for technical debt.

## Expiry Conditions

| Type | Triggers when... | Example |
|------|-------------------|---------|
| `date` | A calendar date has passed | `--expires 2025-06-01` |
| `semver` | Project version meets a threshold | `--semver ">=2.0.0"` |
| `dependency` | A dependency hits a version (or is removed) | `--dependency "react@>=19.0.0"` |

## Quick Start

```bash
# Initialize in your project
python3 ttlnote.py init

# Add a note that expires on a date
python3 ttlnote.py add src/auth.py "Remove OAuth1 workaround" -l 42 -e 2025-06-01 -t debt

# Add a note that triggers at v2.0
python3 ttlnote.py add src/api.py "Delete legacy /v1 endpoints" -s ">=2.0.0"

# Add a note that triggers when a dependency upgrades
python3 ttlnote.py add src/shim.py "Remove React 18 compat shim" -d "react@>=19.0.0"

# Check for expired notes (returns exit code 1 if any expired — great for CI)
python3 ttlnote.py check

# List all notes
python3 ttlnote.py list
python3 ttlnote.py list -t debt        # filter by tag
python3 ttlnote.py list -f src/auth.py  # filter by file

# Remove a resolved note
python3 ttlnote.py remove abc123

# Sweep all expired notes at once
python3 ttlnote.py sweep
```

## Inline Comments

Instead of using the CLI, you can write annotations directly in your source code:

```python
# ttl-note(date=2025-06-01): Remove this workaround [#debt]
result = legacy_hack()
```

```javascript
// ttl-note(semver=>=2.0.0): Delete v1 API compatibility layer
const data = shimV1Response(raw);
```

Then scan your codebase to register them:

```bash
python3 ttlnote.py scan           # scan entire project
python3 ttlnote.py scan src/      # scan specific directory
```

## CI Integration

Add to your CI pipeline to fail builds when tech debt expires:

```yaml
# GitHub Actions
- name: Check expired annotations
  run: python3 ttlnote.py check --quiet
```

The `check` command exits with code 1 when expired notes exist, making it
a natural fit for CI gates. Your team writes the workaround AND the
expiration date, and CI enforces the cleanup.

## How It Works

Notes are stored in a `.ttlnotes` JSON file at your project root. The tool
auto-detects project versions from `package.json`, `pyproject.toml`, or
`Cargo.toml`, and dependency versions from `node_modules` or Python's
`importlib.metadata`.

## Running Tests

```bash
python3 test_ttlnote.py -v
```
