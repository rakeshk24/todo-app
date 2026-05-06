# Coding Guidelines

## Python

- Follow [PEP 8](https://peps.python.org/pep-0008/): 4-space indentation, max line length of 100 characters
- Use snake_case for variables, functions, and module names; PascalCase for classes
- Avoid bare `except` — catch specific exceptions and handle or re-raise them
- Do not suppress errors silently; log or surface them appropriately
- Keep functions focused on a single responsibility

## Security

- Never commit secrets, API keys, or credentials — use environment variables or config files excluded from version control
- Never use the Jinja2 `| safe` filter on user-controlled data
- Always use parameterized queries or ORM methods — never interpolate user input into raw SQL
- Validate and sanitize all input at system boundaries (form submissions, URL parameters, API responses)
- In JavaScript, use `textContent` instead of `innerHTML` when inserting untrusted data into the DOM

## Error Handling

- Validate user input server-side even when client-side validation exists
- Use Flask's `flash()` for user-facing error messages — never expose raw exceptions or stack traces
- Always explicitly commit or rollback database transactions; do not rely on implicit behaviour

## HTML & JavaScript

- No inline styles — use CSS classes
- Avoid `innerHTML` with untrusted or user-supplied content; prefer `textContent` or DOM methods
- Keep JavaScript minimal and scoped — no global state unless necessary
- Use semantic HTML elements where appropriate

## Git

- Write short, imperative commit messages (e.g. `add search filter for todos`, not `added` or `adding`)
- One logical change per commit — avoid mixing unrelated changes
- Branch naming: `feature/`, `fix/`, `chore/` prefixes (e.g. `feature/todo-search`)
- Do not commit generated files, build artifacts, or local config (`.env`, `*.db`, `__pycache__`)

## Dependencies

- Pin all dependency versions in `requirements.txt`
- Do not add a package to solve a one-off problem that can be handled with stdlib
- Review licenses before adding third-party packages

## Database

- Never expose raw database errors to end users
- Keep schema changes additive where possible to avoid data loss
- Document any manual migration steps clearly in the PR description
