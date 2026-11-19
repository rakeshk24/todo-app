# REST API Reference

Base URL: `https://your-domain.example`

Authentication: Pass your API key in the `X-API-Key` header.
If `TODO_API_KEY` is not set, all endpoints are open.

---

## Endpoints

### GET /api/todos

List todos with pagination.

**Query params:**

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number (1–1,000,000) |
| `per_page` | 20 | Items per page (1–100) |

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Buy milk",
    "description": "From the corner shop",
    "deadline": "2026-11-25 10:00",
    "completed": false,
    "completed_at": null,
    "created_at": "2026-11-19 09:00",
    "priority": "high"
  }
]
```

**Error responses:**

| Status | Meaning |
|--------|---------|
| 400 | Invalid pagination parameters |
| 401 | Missing or invalid API key |

---

### GET /api/todos/:id

Get a single todo by ID.

**Response `200 OK`:** Same object shape as list items.

**Error `404`:**
```json
{"error": "Todo not found"}
```

---

### POST /api/todos

Create a new todo.

**Request body (JSON):**
```json
{
  "title": "Buy milk",
  "description": "Optional description",
  "deadline": "2026-11-25T10:00"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | ✓ | Max 200 chars |
| `description` | string | ✓ | Can be empty string |
| `deadline` | string | ✗ | Format: `YYYY-MM-DDTHH:MM` |

**Response `201 Created`:** Full todo object.

**Error responses:**

| Status | Reason |
|--------|--------|
| 400 | Missing/invalid title or description |
| 400 | Invalid deadline format |
| 401 | Missing or invalid API key |

---

## Export Endpoint

### GET /export

Export all todos as JSON. Requires the `X-Export-Key` header.

**Response:** Array of todo objects (all fields including priority).

---

## Examples

```bash
# List todos
curl https://your-domain.example/api/todos \
  -H "X-API-Key: <your-key>"

# Get a specific todo
curl https://your-domain.example/api/todos/42 \
  -H "X-API-Key: <your-key>"

# Create a todo
curl -X POST https://your-domain.example/api/todos \
  -H "X-API-Key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish report","description":"Q4 summary","deadline":"2026-11-30T17:00"}'
```
