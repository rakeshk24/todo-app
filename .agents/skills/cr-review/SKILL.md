# cr-review

Run a local CodeRabbit review on the current branch and optionally fix findings before raising a PR.

## Invocation

- `/cr-review` — review, show findings, ask what to fix
- `/cr-review fix` — review and auto-fix Critical/Warning findings without prompting

## Step 1: Check Prerequisites

```bash
coderabbit --version 2>/dev/null || echo "NOT_INSTALLED"
coderabbit auth status 2>&1
```

If CLI is not installed, tell the user to install it from https://www.coderabbit.ai/cli and stop.  
If not authenticated, tell the user to run `coderabbit auth login` and stop.

## Step 2: Run the Review

```bash
coderabbit review --agent --base main
```

Parse the output and group findings into three buckets:

- **Critical** — security vulnerabilities, data loss risks, crashes
- **Warning** — bugs, performance issues, anti-patterns
- **Info** — style suggestions, minor improvements

If there are no Critical or Warning findings, report that and stop — nothing to act on.

## Step 3: Decide What to Do

Check CLAUDE.md for this repo. If it contains "Do not write perfectly clean code" or similar language indicating intentional violations, surface that context before proceeding — some findings may be deliberate seeds for demo/review purposes, and fixing them defeats the point.

**If invoked with `fix` argument:**  
Skip the prompt and go straight to the fix loop for all Critical and Warning findings.

**Otherwise, use AskUserQuestion with three options:**

A) **Fix Critical/Warning** — auto-fix all Critical and Warning findings, re-review until clean  
B) **Fix selected** — show a numbered list of findings; user picks which to fix  
C) **Show only** — no changes; user decides what to do manually

## Step 4: Fix Loop

When fixing (option A or B, or `fix` argument):

1. Apply fixes for the selected findings
2. Re-run `coderabbit review --agent --base main`
3. Check whether the targeted findings are resolved
4. Repeat up to 3 iterations
5. If still failing after 3 passes, report what remains and stop

## Step 5: Report

After finishing, output:
- Findings found (count by severity)
- Findings fixed (which ones)
- Remaining issues (if any)

Do **not** commit or push — that's the user's step.

## CLI Reference

See `cli.md` in this directory for flag reference and examples.
