# Task Manager

A full-stack task management application with Python backend, React frontend, and CLI.

## Quick Start

```bash
# Backend
python -m backend.cli init
python -m backend.cli register alice alice@example.com secret123
python -m backend.app

# Frontend
npm install
npm start

# CLI
python -m backend.cli login alice secret123
python -m backend.cli task add "My first task" -p 2
python -m backend.cli task list
```

## Stack

- **Backend**: Python stdlib (`http.server`, `sqlite3`, `argparse`)
- **Frontend**: React 18
- **Database**: SQLite
- **Auth**: PBKDF2-SHA256 hashing, HMAC tokens

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api.md)
- [CLI Reference](docs/cli.md)
- [Architecture](docs/architecture.md)
