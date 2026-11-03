# CodeRabbit CLI Reference

## Check setup
```bash
coderabbit --version 2>/dev/null || echo "NOT_INSTALLED"
coderabbit auth status 2>&1
```

## Run review

Agent mode (structured output for Claude to parse):
```bash
coderabbit review --agent --base main
```

Plain mode (human-readable with fix suggestions):
```bash
coderabbit review --plain --base main
```

## Useful flags

| Flag | Description |
|------|-------------|
| `--base main` | Compare against main branch |
| `--agent` | Minimal output optimised for AI agents |
| `--plain` | Detailed output with fix suggestions |
| `--deep` | Deeper review using the GitHub PR review policy (CLI 0.8.0+) |
| `--gate <severity>` | Exit code 2 if findings at/above severity (use with `--agent`) |
| `-t committed` | Committed changes only |
| `-t uncommitted` | Uncommitted changes only |
| `-t all` | All changes (default) |
| `--include-untracked` | Also review untracked files (combine with `-t uncommitted`) |
| `--remote owner/repo` | Review without a local checkout (CLI 0.7.7+) |

## Deep mode

`--deep` runs a more thorough review using the same policy as GitHub PR reviews. Requires CLI 0.8.0+.

```bash
coderabbit review --deep --agent --base main
```

Note: deep mode does not attach to an existing PR — findings may differ from what you see on the PR itself.

`cr` is an alias for `coderabbit`.
