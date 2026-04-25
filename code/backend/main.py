import argparse
import json
import sys

from .config import DATABASE_URL
from .database import init_db
from .services.auth import create_user, authenticate
from .services import (
    create_task,
    get_task_by_id,
    list_user_tasks,
    update_task_status,
    delete_task,
    get_task_stats,
)

TOKEN_FILE = ".tasktoken"


def _save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def _load_token() -> str | None:
    try:
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def _require_token() -> str:
    token = _load_token()
    if not token:
        print("Not logged in. Run: taskmgr login <username> <password>")
        sys.exit(1)
    return token


def _get_user_id(token: str) -> int:
    try:
        return int(token.split(":")[0])
    except (ValueError, IndexError):
        print("Invalid token. Please log in again.")
        sys.exit(1)


def cmd_init(args):
    init_db()
    print("Database initialized.")


def cmd_config(args):
    print(f"Database URL: {DATABASE_URL}")


def cmd_register(args):
    try:
        user = create_user(args.username, args.email, args.password)
        print(f"User '{user.username}' created (id={user.id})")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_login(args):
    token = authenticate(args.username, args.password)
    if not token:
        print("Invalid credentials.")
        sys.exit(1)
    _save_token(token)
    print(f"Logged in as {args.username}.")


def cmd_task_add(args):
    token = _require_token()
    user_id = _get_user_id(token)
    task = create_task(user_id, args.title, args.description or "", args.priority)
    print(f"Task created: #{task.id} - {task.title}")


def cmd_task_list(args):
    token = _require_token()
    user_id = _get_user_id(token)
    tasks = list_user_tasks(user_id, args.status)
    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        print(f"  #{t.id} [{t.status}] P{t.priority} - {t.title}")


def cmd_task_status(args):
    token = _require_token()
    user_id = _get_user_id(token)
    try:
        task = update_task_status(args.task_id, args.status)
        print(f"Task #{task.id} status updated to '{task.status}'")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_task_delete(args):
    token = _require_token()
    deleted = delete_task(args.task_id)
    if deleted:
        print(f"Task #{args.task_id} deleted.")
    else:
        print(f"Task #{args.task_id} not found.")


def cmd_task_stats(args):
    token = _require_token()
    user_id = _get_user_id(token)
    stats = get_task_stats(user_id)
    print(f"Task Statistics (total: {stats['total']})")
    for status, count in stats.items():
        if status != "total":
            print(f"  {status}: {count}")


def build_parser():
    parser = argparse.ArgumentParser(prog="taskmgr", description="Task Manager CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize the database")

    sub.add_parser("config", help="Show current configuration")

    reg = sub.add_parser("register", help="Register a new user")
    reg.add_argument("username")
    reg.add_argument("email")
    reg.add_argument("password")

    login = sub.add_parser("login", help="Login to an account")
    login.add_argument("username")
    login.add_argument("password")

    task = sub.add_parser("task", help="Task operations")
    task_sub = task.add_subparsers(dest="task_command")

    add = task_sub.add_parser("add", help="Add a new task")
    add.add_argument("title")
    add.add_argument("--description", "-d", default="")
    add.add_argument("--priority", "-p", type=int, default=1)

    ls = task_sub.add_parser("list", help="List tasks")
    ls.add_argument("--status", "-s", default=None)

    status = task_sub.add_parser("status", help="Update task status")
    status.add_argument("task_id", type=int)
    status.add_argument("status")

    delete = task_sub.add_parser("delete", help="Delete a task")
    delete.add_argument("task_id", type=int)

    task_sub.add_parser("stats", help="Show task statistics")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "config": cmd_config,
        "register": cmd_register,
        "login": cmd_login,
    }
    task_commands = {
        "add": cmd_task_add,
        "list": cmd_task_list,
        "status": cmd_task_status,
        "delete": cmd_task_delete,
        "stats": cmd_task_stats,
    }

    if args.command in commands:
        commands[args.command](args)
    elif args.command == "task" and args.task_command in task_commands:
        task_commands[args.task_command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
