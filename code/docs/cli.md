# CLI Reference

The `taskmgr` CLI manages tasks from the terminal.

## Usage

```bash
python -m backend.cli <command> [arguments]
```

## Commands

### init

Initialize the SQLite database and create tables.

```bash
python -m backend.cli init
```

### config

Show current configuration.

```bash
python -m backend.cli config
```

### register

Create a new user account.

```bash
python -m backend.cli register <username> <email> <password>
```

### login

Authenticate and store a token in `.tasktoken`.

```bash
python -m backend.cli login <username> <password>
```

## Task Subcommands

All task commands require a valid `.tasktoken` file (created by `login`).

### task add

Create a new task.

```bash
python -m backend.cli task add <title> [--description TEXT] [--priority 1|2|3]
```

| Option          | Alias | Default | Description       |
|----------------|-------|---------|-------------------|
| `--description` | `-d`  | `""`    | Task description  |
| `--priority`    | `-p`  | `1`     | Priority (1-3)    |

### task list

List tasks for the logged-in user.

```bash
python -m backend.cli task list [--status STATUS]
```

| Option     | Alias | Default  | Description                   |
|-----------|-------|----------|-------------------------------|
| `--status` | `-s`  | all      | Filter by status              |

### task status

Update a task's status. Valid transitions:

| From         | To                         |
|-------------|----------------------------|
| pending      | in_progress, cancelled     |
| in_progress  | completed, cancelled       |
| completed    | in_progress                |
| cancelled    | pending                    |

```bash
python -m backend.cli task status <task_id> <status>
```

### task delete

Delete a task.

```bash
python -m backend.cli task delete <task_id>
```

### task stats

Show task counts grouped by status.

```bash
python -m backend.cli task stats
```

## Examples

```bash
# Setup
python -m backend.cli init
python -m backend.cli register alice alice@example.com secret123
python -m backend.cli login alice secret123

# Task management
python -m backend.cli task add "Fix login bug" -d "Session expires immediately" -p 3
python -m backend.cli task list
python -m backend.cli task status 1 in_progress
python -m backend.cli task stats
python -m backend.cli task delete 1
```
