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
| `-t committed` | Committed changes only |
| `-t uncommitted` | Uncommitted changes only |
| `-t all` | All changes (default) |

`cr` is an alias for `coderabbit`.
