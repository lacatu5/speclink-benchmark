# Getting Started

## Prerequisites

- Python 3.10+
- Node.js 16+
- npm

## Backend Setup

1. Initialize the database:

```bash
python -m backend.main init
```

2. Create a user account:

```bash
python -m backend.main register alice alice@example.com secret123
```

3. Start the API server:

```bash
python -m backend.app
```

The server runs on `http://localhost:8010` by default. Configure host and port in `backend/config.py`.

## Frontend Setup

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm start
```

The app runs on `http://localhost:3000` and proxies API requests to the backend.

## CLI Usage

Login and manage tasks from the terminal:

```bash
python -m backend.main login alice secret123
python -m backend.main task add "Write tests" -p 2
python -m backend.main task list
python -m backend.main task status 1 in_progress
python -m backend.main task stats
```

## Configuration

All configuration is in `backend/config.py`:

| Variable            | Default                   | Description                    |
|--------------------|---------------------------|--------------------------------|
| DATABASE_URL       | `sqlite:///tasks.db`      | SQLite database path           |
| SECRET_KEY         | `dev-secret-key-change-in-production` | HMAC key for token signing     |
| DEBUG              | `False`                   | Enable HTTP request logging    |
| HOST               | `0.0.0.0`                 | Server bind address            |
| PORT               | `8015`                    | Server bind port               |
| TOKEN_EXPIRY_HOURS | `24`                      | Token validity period          |
| MAX_TASKS_PER_USER | `100`                     | Max tasks per user             |

## Environment Variables

The frontend reads:

- `REACT_APP_API_URL`: API base URL (default: `http://localhost:8001/api`)
