# API Reference

Base URL: `http://localhost:8001/api`

All endpoints except auth routes require an `Authorization: Bearer <token>` header.

## Authentication

### POST /api/auth/register

Create a new user account.

**Request body:**

| Field     | Type   | Required |
|-----------|--------|----------|
| username  | string | yes      |
| email     | string | yes      |
| password  | string | yes      |

**Response `201`:**

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2025-01-15T10:30:00"
}
```

### POST /api/auth/login

Authenticate and receive a token.

**Request body:**

| Field     | Type   | Required |
|-----------|--------|----------|
| username  | string | yes      |
| password  | string | yes      |

**Response `200`:**

```json
{
  "token": "1:2025-01-15T10:30:00:abc123def456"
}
```

**Error `401`:**

```json
{
  "error": "Invalid credentials"
}
```

## Tasks

### POST /api/tasks

Create a new task. Requires authentication.

**Request body:**

| Field        | Type   | Required | Default |
|-------------|--------|----------|---------|
| title        | string | yes      |         |
| description  | string | no       | `""`    |
| priority     | int    | no       | `1`     |

Priority must be `1` (Low), `2` (Medium), or `3` (High).

**Response `201`:**

```json
{
  "id": 1,
  "user_id": 1,
  "title": "Fix bug",
  "description": "Critical login bug",
  "status": "pending",
  "priority": 3,
  "created_at": "2025-01-15T10:35:00",
  "updated_at": null
}
```

### GET /api/tasks

List all tasks for the authenticated user. Optional `?status=pending` filter.

**Response `200`:**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Fix bug",
    "description": "Critical login bug",
    "status": "pending",
    "priority": 3,
    "created_at": "2025-01-15T10:35:00",
    "updated_at": null
  }
]
```

Tasks are ordered by priority descending, then created_at descending.

### GET /api/tasks/stats

Get task counts grouped by status for the authenticated user.

**Response `200`:**

```json
{
  "pending": 2,
  "in_progress": 1,
  "completed": 5,
  "cancelled": 0,
  "total": 8
}
```

### PATCH /api/tasks/:id/status

Update a task's status. Valid status transitions:

| From         | To                         |
|-------------|----------------------------|
| pending      | in_progress, cancelled     |
| in_progress  | completed, cancelled       |
| completed    | in_progress                |
| cancelled    | pending                    |

**Request body:**

| Field  | Type   | Required |
|--------|--------|----------|
| status | string | yes      |

Valid statuses: `pending`, `in_progress`, `completed`, `cancelled`.

**Response `200`:**

```json
{
  "id": 1,
  "user_id": 1,
  "title": "Fix bug",
  "description": "Critical login bug",
  "status": "in_progress",
  "priority": 3,
  "created_at": "2025-01-15T10:35:00",
  "updated_at": "2025-01-15T11:00:00"
}
```

### DELETE /api/tasks/:id

Delete a task by ID.

**Response `200`:**

```json
{
  "deleted": true
}
```

**Error `404`:**

```json
{
  "error": "Task not found"
}
```
