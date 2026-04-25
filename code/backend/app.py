import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

from .config import HOST, PORT, DEBUG
from .database import init_db
from .services.auth import create_user, authenticate
from .services.tasks import (
    create_task,
    get_task_by_id,
    list_user_tasks,
    update_task_status,
    delete_task,
    get_task_stats,
)


def extract_user_id(token: str) -> int | None:
    try:
        parts = token.split(":")
        return int(parts[0])
    except (ValueError, IndexError):
        return None


class TaskAPIHandler(BaseHTTPRequestHandler):
    routes = {}

    @classmethod
    def register_route(cls, method, pattern):
        def decorator(func):
            cls.routes[(method, pattern)] = func
            return func
        return decorator

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def _get_token(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    def _require_auth(self):
        token = self._get_token()
        if not token:
            self._send_json({"error": "Missing authorization token"}, 401)
            return None
        user_id = extract_user_id(token)
        if not user_id:
            self._send_json({"error": "Invalid token"}, 401)
            return None
        return user_id

    def _match_route(self, method):
        path = self.path.rstrip("/") or "/"
        for (route_method, pattern), handler in self.routes.items():
            if route_method != method:
                continue
            match = re.fullmatch(pattern, path)
            if match:
                return handler, match.groupdict()
        return None, {}

    def do_GET(self):
        handler, params = self._match_route("GET")
        if handler:
            handler(self, **params)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        handler, params = self._match_route("POST")
        if handler:
            handler(self, **params)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_PATCH(self):
        handler, params = self._match_route("PATCH")
        if handler:
            handler(self, **params)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        handler, params = self._match_route("DELETE")
        if handler:
            handler(self, **params)
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        if DEBUG:
            super().log_message(format, *args)


def register_routes():
    @TaskAPIHandler.register_route("POST", r"/api/auth/register")
    def handle_register(handler):
        body = handler._read_body()
        try:
            user = create_user(
                body["username"], body["email"], body["password"]
            )
            handler._send_json(user.to_dict(), 201)
        except Exception as e:
            handler._send_json({"error": str(e)}, 400)

    @TaskAPIHandler.register_route("POST", r"/api/auth/login")
    def handle_login(handler):
        body = handler._read_body()
        token = authenticate(body.get("username", ""), body.get("password", ""))
        if token:
            handler._send_json({"token": token})
        else:
            handler._send_json({"error": "Invalid credentials"}, 401)

    @TaskAPIHandler.register_route("POST", r"/api/tasks")
    def handle_create_task(handler):
        user_id = handler._require_auth()
        if user_id is None:
            return
        body = handler._read_body()
        try:
            task = create_task(
                user_id,
                body["title"],
                body.get("description", ""),
                body.get("priority", 1),
            )
            handler._send_json(task.to_dict(), 201)
        except Exception as e:
            handler._send_json({"error": str(e)}, 400)

    @TaskAPIHandler.register_route("GET", r"/api/tasks")
    def handle_list_tasks(handler):
        user_id = handler._require_auth()
        if user_id is None:
            return
        status = handler.path.query_string if hasattr(handler.path, "query_string") else None
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(handler.path)
        params = parse_qs(parsed.query)
        status = params.get("status", [None])[0]
        tasks = list_user_tasks(user_id, status)
        handler._send_json([t.to_dict() for t in tasks])

    @TaskAPIHandler.register_route("GET", r"/api/tasks/stats")
    def handle_task_stats(handler):
        user_id = handler._require_auth()
        if user_id is None:
            return
        stats = get_task_stats(user_id)
        handler._send_json(stats)

    @TaskAPIHandler.register_route("PATCH", r"/api/tasks/(?P<task_id>\d+)/status")
    def handle_update_status(handler, task_id):
        user_id = handler._require_auth()
        if user_id is None:
            return
        body = handler._read_body()
        try:
            task = update_task_status(int(task_id), body["status"])
            handler._send_json(task.to_dict())
        except ValueError as e:
            handler._send_json({"error": str(e)}, 400)

    @TaskAPIHandler.register_route("DELETE", r"/api/tasks/(?P<task_id>\d+)")
    def handle_delete_task(handler, task_id):
        user_id = handler._require_auth()
        if user_id is None:
            return
        deleted = delete_task(int(task_id))
        if deleted:
            handler._send_json({"deleted": True})
        else:
            handler._send_json({"error": "Task not found"}, 404)


def create_app():
    init_db()
    register_routes()
    return TaskAPIHandler


def main():
    handler = create_app()
    server = HTTPServer((HOST, PORT), handler)
    print(f"Server running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
