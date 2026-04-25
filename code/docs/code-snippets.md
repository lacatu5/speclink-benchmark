# Code Snippets

This document walks through key code patterns used in the project.

## Password Hashing

Passwords are hashed using PBKDF2-SHA256 with a random 16-byte salt. The salt and hash are stored together as a single string.

```python
import hashlib
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    hashed = hashlib.scrypt(
        password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32
    )
    return f"{salt.hex()}:{hashed.hex()}"
```

Verification compares the stored hash against a fresh hash of the input using constant-time comparison to prevent timing attacks:

```python
import hmac

def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, stored_hash = password_hash.split(":")
    hashed = hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt_hex), n=16384, r=8, p=1, dklen=32
    )
    return hmac.compare_digest(hashed.hex(), stored_hash)
```

## Token Generation

Tokens are HMAC-signed strings containing the user ID and timestamp. The signature prevents tampering since only the server knows `SECRET_KEY`.

```python
def generate_token(user_id: int) -> str:
    payload = f"{user_id}:{datetime.utcnow().isoformat()}"
    signature = hmac.new(
        SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"
```

On the server side, `extract_user_id` parses the token to identify the caller:

```python
def extract_user_id(token: str) -> int | None:
    try:
        parts = token.split(":")
        return int(parts[0])
    except (ValueError, IndexError):
        return None
```

## Status Transition Guard

The `Task` model enforces a state machine. Only valid transitions are allowed:

```python
def can_transition_to(self, new_status: str) -> bool:
    transitions = {
        "pending": ("in_progress", "cancelled"),
        "in_progress": ("completed", "cancelled"),
        "completed": ("in_progress",),
        "cancelled": ("pending",),
    }
    return new_status in transitions.get(self.status, ())
```

The `update_task_status` service function checks this before writing to the database:

```python
if not task.can_transition_to(new_status):
    raise ValueError(
        f"Cannot transition from {task.status} to {new_status}"
    )
```

## API Route Registration

Routes are registered using decorators with regex patterns. Named groups become keyword arguments to the handler:

```python
@TaskAPIHandler.register_route("PATCH", r"/api/tasks/(?P<task_id>\d+)/status")
def handle_update_status(handler, task_id):
    user_id = handler._require_auth()
    if user_id is None:
        return
    body = handler._read_body()
    task = update_task_status(int(task_id), body["status"])
    handler._send_json(task.to_dict())
```

The `_match_route` method iterates all registered routes and uses `re.fullmatch` to find a handler:

```python
def _match_route(self, method):
    path = self.path.rstrip("/") or "/"
    for (route_method, pattern), handler in self.routes.items():
        if route_method != method:
            continue
        match = re.fullmatch(pattern, path)
        if match:
            return handler, match.groupdict()
    return None, {}
```

## React Task Hook

The `useTasks` hook encapsulates all task operations with loading and error state:

```javascript
export function useTasks(initialStatus = null) {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addTask = useCallback(async (title, description, priority) => {
    const task = await api.createTask(title, description, priority);
    setTasks((prev) => [task, ...prev]);
    return task;
  }, []);

  const changeStatus = useCallback(async (taskId, status) => {
    const updated = await api.updateTaskStatus(taskId, status);
    setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    return updated;
  }, []);

  useEffect(() => {
    refresh(initialStatus);
  }, [refresh, initialStatus]);

  return { tasks, stats, loading, error, refresh, loadStats, addTask, changeStatus, remove };
}
```

Mutations update local state optimistically — `addTask` prepends to the list, `changeStatus` replaces the matching task, and `remove` filters it out.

## API Client Error Handling

The `request` function centralizes auth header injection and error checking:

```javascript
async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}
```

## CLI Token Storage

The CLI stores tokens in a local `.tasktoken` file. Commands that require auth call `_require_token` which exits with a message if no token exists:

```python
def _require_token() -> str:
    token = _load_token()
    if not token:
        print("Not logged in. Run: taskmgr login <username> <password>")
        sys.exit(1)
    return token
```

The user ID is extracted from the token by splitting on `:` and taking the first segment:

```python
def _get_user_id(token: str) -> int:
    try:
        return int(token.split(":")[0])
    except (ValueError, IndexError):
        print("Invalid token. Please log in again.")
        sys.exit(1)
```

## Task Statistics Aggregation

The `get_task_stats` function, which grouped tasks by status and filled in zero counts for statuses with no tasks, has been removed from the codebase.

