# Todo Sorting & Priority

## Priority Levels

Each todo can have one of four priority levels:

| Level  | Description |
|--------|-------------|
| High   | Urgent tasks that need immediate attention |
| Medium | Normal priority tasks |
| Low    | Nice-to-have, non-blocking tasks |
| None   | No priority assigned (default) |

Priority is set when creating or editing a todo.

## Sort Options

The todo list can be sorted by:

- **Priority** — High → Medium → Low → None (default sort)
- **Deadline** — earliest deadline first
- **Created** — newest first
- **Title** — alphabetical

Sort direction can be toggled between ascending (↑) and descending (↓).

## Sort Parameters

Sort state is preserved in the URL as query parameters:

```
/?sort_by=priority&direction=asc
/?sort_by=deadline&direction=desc&assignee=user@example.com
```

| Parameter   | Values                             | Default    |
|-------------|-------------------------------------|------------|
| `sort_by`   | `priority`, `deadline`, `created`, `title` | `priority` |
| `direction` | `asc`, `desc`                       | `asc`      |

## Implementation

Sorting logic lives in `utils/sorting.py`. The `sort_todos()` function accepts a list of Todo
objects and returns them sorted according to the specified criteria.

Priority ordering is defined in `PRIORITY_ORDER` within that module.

Default values (DEFAULT_SORT, DEFAULT_DIRECTION, PRIORITY_LEVELS) are in `config/defaults.py`.
