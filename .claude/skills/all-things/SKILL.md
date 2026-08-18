---
name: all-things
description: Generate 3 CodeRabbit-exercise feature ideas for this todo app, let the user pick one, implement it on a new branch, push to remote, and output a Jira ticket description
version: 0.1.0
triggers:
  - all-things
  - all.?things
---

# all-things

Generate 3 fresh feature ideas for the todo app designed to exercise specific CodeRabbit review behaviors. The user picks one; you implement it, push to remote, and output a ready-to-paste Jira ticket description.

## Step 0: Read Source of Truth

Before generating any ideas, read these files:

1. `.coderabbit.yaml` — extract:
   - `reviews.pre_merge_checks.custom_checks` (names, modes, instructions)
   - `reviews.path_instructions` (review dimensions enforced)
   - `reviews.finishing_touches.custom` (names, instructions)
   - `knowledge_base.jira.project_keys`
2. `CODING_GUIDELINES.md` — extract all rules
3. `app.py`, `templates/index.html`, `templates/edit.html`, `static/style.css` — understand current feature set so ideas extend it naturally

## Step 1: Generate 3 Ideas

Generate exactly 3 distinct feature ideas. Each must be genuinely useful for the todo app (not contrived), and each must satisfy **all 6 criteria** below without exception. Do not reuse the same violation pattern across all 3 ideas — vary which custom check and which guideline violations appear in each.

### The 6 Non-Negotiable Criteria

**Criterion 1 — Violate ≥1 custom pre-merge check**

Every idea must trigger at least one of the custom checks found in `.coderabbit.yaml`. Common patterns:

- _"PII and sensitive data in logs"_: a `print()` or log call that outputs todo content (title, description) combined with any user identifier (email, username, IP) without masking.
- _"Security checks"_: hardcoded credential/path in source, user input passed unsanitized to a query or shell call, an endpoint with no ownership/auth check, TLS verification disabled.

The idea description must name the specific check(s) it triggers and show the offending line(s) of code that will be written.

**Criterion 2 — Qualify for a sequence diagram**

The idea must be a **new feature or significant control-flow change** that:
- Involves **3 or more interacting components** (e.g. Flask route, SQLAlchemy model, helper module, Jinja2 template, JavaScript, external API, a second model)
- Has a **genuinely sequential flow** worth visualizing (A calls B, B calls C, C returns to B, B returns to A)
- Is **NOT** a bug fix, refactor, config/doc/test-only change, simple one-table CRUD on 1–2 files

The idea description must list the components and describe the sequential flow in one sentence.

**Criterion 3 — Generate ≥3 CodeRabbit inline comments**

The implementation must deliberately introduce ≥3 distinct violations of `CODING_GUIDELINES.md` or the `path_instructions` review dimensions. Each violation must be specific and different. Seed from this list (do not use fewer than 3):

- Bare `except` or `except Exception` with no logging — violates guidelines + correctness dimension
- Silent redirect instead of `flash()` on a validation failure — violates guidelines + correctness dimension
- Inline `style="..."` attribute in a template — violates guidelines (no inline styles)
- `innerHTML` used to insert untrusted/user-sourced content into the DOM — violates guidelines + security dimension
- No server-side validation on a new input field (length, type, enum range) — violates guidelines + security dimension
- DB query with no result-size limit on a table that grows unboundedly — violates performance dimension
- New route or business-logic branch with zero test coverage noted — violates testing dimension
- A new public function with no type hints and undocumented side effects — violates maintainability dimension

The idea description must list each planned violation with the file and approximate location.

**Criterion 4 — Leave room for the `harden security` finishing touch**

The intentional issues seeded by Criteria 1 and 3 must overlap with what the `harden security` finishing touch is designed to fix (redact PII from logs, remove hardcoded secrets/paths, validate/sanitize input, fix auth gaps). At least 2 of the seeded violations must be in the `harden security` fix scope.

The idea description must confirm which violations the finishing touch would address.

**Criterion 5 — Include a Jira ticket description**

Each idea must include a ready-to-paste Jira description using the project key(s) from `.coderabbit.yaml`. Format:

```
Project: <key from .coderabbit.yaml>
Issue Type: Story
Summary: <short imperative title>
Description:
  As a <user/developer>, I want <feature> so that <value>.
Acceptance Criteria:
  - [ ] <criterion 1>
  - [ ] <criterion 2>
  - [ ] <criterion 3>
Labels: feature, todo-app
```

**Criterion 6 — Config is always read first (enforced by Step 0)**

Ideas are calibrated to the live `.coderabbit.yaml`, not hardcoded assumptions. If the config changes between invocations, the ideas adapt.

### Presenting the 3 Ideas

For each idea present:

1. **Feature name** (short, imperative)
2. **What it does** (2–3 sentences, user-facing value)
3. **Files changed** (list each file)
4. **Sequential flow** (one sentence, names the 3+ components)
5. **Custom check(s) triggered** (name + the offending line that will be written)
6. **Planned violations** (bulleted list: violation → file → why CR will flag it)
7. **Finishing touch coverage** (which violations `harden security` addresses)
8. **Jira ticket description** (full block as per Criterion 5 format)

## Step 2: Ask User to Pick

Use `AskUserQuestion` with the 3 ideas as options. Label them A, B, C.

## Step 3: Implement

After the user picks:

1. Create a new branch: `feature/<kebab-case-feature-name>` off `main`
2. Implement the feature following the plan from Step 1 for that idea:
   - Write genuinely functional code — the feature must work end-to-end
   - Seed the planned violations exactly as described (do not fix them)
   - Touch ≥3 files to ensure the sequence diagram qualifies
3. Commit with a short imperative message (≤5 words, no attribution)
4. Push: `git push -u origin <branch>`

## Step 4: Output

After pushing, output:

1. The branch name and push confirmation
2. A reminder to open a PR manually and link the Jira ticket in the PR description
3. The full Jira ticket description (from the chosen idea) ready to copy-paste

## Key Constraints

- Do not fix the seeded violations — they are intentional (see `CLAUDE.md`: "Do not write perfectly clean code")
- Do not add comments explaining the intentional issues
- Branch naming: `feature/` prefix, kebab-case
- Commit messages: short, imperative, ≤5 words, no "Generated by Claude" or similar
- Do not open the PR — the user does that manually
