# Architecture

## Overview

Task Manager is a full-stack application with a Python backend, React frontend, and shared REST API.

```
speclink-benchmark/
├── backend/
│   ├── __init__.py
│   ├── app.py              # HTTP server and route handlers
│   ├── cli.py              # argparse CLI
│   ├── config.py           # Configuration constants
│   ├── database.py         # SQLite connection and schema
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py         # Task dataclass
│   │   └── user.py         # User dataclass
│   └── services/
│       ├── __init__.py
│       ├── auth.py         # Authentication and password hashing
│       └── tasks.py        # Task CRUD and stats
├── frontend/
│   └── src/
│       ├── api/
│       │   └── client.js   # API request functions
│       ├── hooks/
│       │   ├── useAuth.js   # Authentication state hook
│       │   └── useTasks.js  # Task state management hook
│       ├── components/
│       │   ├── LoginForm.jsx
│       │   ├── Dashboard.jsx
│       │   └── TaskList.jsx
│       ├── utils/
│       │   └── helpers.js   # Formatting utilities
│       ├── App.jsx
│       └── index.jsx
├── docs/
│   ├── api.md
│   ├── cli.md
│   ├── architecture.md
│   └── getting-started.md
├── package.json
└── README.md
```

## Backend

The backend uses Python's built-in `http.server` module with no external framework dependencies.

### HTTP Server (`app.py`)

`TaskAPIHandler` extends `BaseHTTPRequestHandler`. Routes are registered via the `@register_route(method, pattern)` decorator which matches URL patterns using `re.fullmatch`. Path parameters are captured with named groups like `(?P<task_id>\d+)`.

The server is started with `python -m backend.app`, which calls `main()`. This initializes the database, registers routes, and starts `HTTPServer` on the configured host and port.

### CLI (`cli.py`)

Uses `argparse` with nested subcommands. Authentication state is stored in a local `.tasktoken` file. The token format is `{user_id}:{timestamp}:{signature}`, so the CLI extracts the user ID by splitting on `:` and taking the first part.

### Database (`database.py`)

SQLite via `sqlite3` with `row_factory = sqlite3.Row` for dict-like row access. Two tables:

- **users**: id, username (unique), email (unique), password_hash, created_at
- **tasks**: id, user_id (FK → users.id ON DELETE CASCADE), title, description, status, priority, created_at, updated_at

### Models

- **User** (`models/user.py`): Dataclass with `to_dict()` (excludes password_hash) and `from_row()` class method.
- **Task** (`models/task.py`): Dataclass with status transition logic via `can_transition_to()`. Valid statuses: `pending`, `in_progress`, `completed`, `cancelled`. Valid priorities: `1`, `2`, `3`.

### Services

- **auth** (`services/auth.py`): PBKDF2-SHA256 password hashing with HMAC-based token generation. Token format: `{user_id}:{timestamp}:{hmac_signature}`.
- **tasks** (`services/tasks.py`): CRUD operations with status transition validation. `get_task_stats()` returns counts grouped by status.

## Frontend

React 18 single-page application using function components and hooks.

### API Client (`api/client.js`)

Wraps `fetch` with automatic JSON parsing, Bearer token injection from `localStorage`, and error handling. The base URL comes from `REACT_APP_API_URL` env var, defaulting to `http://localhost:8001/api`.

### Hooks

- **useAuth**: Manages `register`, `login`, `logout` with loading/error state. On login, stores token in localStorage.
- **useTasks**: Manages task list, stats, and mutations (`addTask`, `changeStatus`, `remove`). Auto-fetches tasks on mount.

### Components

- **LoginForm**: Toggle between login/register modes. Fields: username, email (register only), password.
- **Dashboard**: Shows stats bar, add-task form, and task list. Loads stats via `useTasks`.
- **TaskList**: Renders task items with status dropdown and delete button.
- **App**: Root component. Shows `LoginForm` when unauthenticated, `Dashboard` when authenticated.

## Authentication Flow

1. Client calls `POST /api/auth/register` or `POST /api/auth/login`
2. Server returns a token: `{user_id}:{timestamp}:{hmac_signature}`
3. Client stores token in `localStorage` (web) or `.tasktoken` (CLI)
4. Subsequent requests include `Authorization: Bearer <token>` header
5. Server extracts user_id from token's first segment
