# Jira Automation Scripts

Python scripts for automating Jira ticket management and status tracking.

## Setup

1. **Install dependencies** with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Jira credentials and settings
   - Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Scripts

### `jira_status.py`
Displays all your tickets grouped by status for the current sprint.

**Usage:**
```bash
uv run python jira_status.py
```

**Output:**
- Shows tickets organized by status (Open, In Progress, In Queue, etc.)
- Displays count for each status
- Lists ticket keys and summaries

### `jira_updates.py`
Automates daily ticket management tasks.

**Features:**
1. Adds comments to all 'Open' tickets acknowledging them
2. Moves specified tickets to 'In Queue' with context about current work

**Usage:**
```bash
# Preview mode (shows what would happen without making changes)
uv run python jira_updates.py

# To actually make changes, edit the file and set:
MAKE_TICKET_UPDATES = True
```

**Configuration:**
Edit the `TICKETS_TO_QUEUE` array in the script:
```python
TICKETS_TO_QUEUE = [
    'PROPERTY-2596',
    'PROPERTY-2595',
]
```

## Files

### Entry points
- `jira` - launcher for the main menu (`./jira`)
- `jira_main.py` - main menu linking the three tools below
- `jira_updates.py` - daily ticket updates
- `jira_time.py` - view and log time
- `jira_status.py` - tickets grouped by status

### Modules
- `jira_lib/` - Jira connection, queries, worklogs and session
- `controllers/` - business logic for status, time and workflow (no printing)
- `ui/` - terminal views, menus and formatting
- `config.py` - configuration loaded from environment variables
- `tests/` - offline tests for the pure helpers

### Configuration
- `.env` - Your credentials (DO NOT COMMIT)
- `.env.example` - Template for environment variables
- `.gitignore` - Protects sensitive files

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_URL` | Your Jira instance URL | `https://your-domain.atlassian.net` |
| `JIRA_EMAIL` | Your Jira email | `you@example.com` |
| `JIRA_API_TOKEN` | Your API token | Generated from Atlassian |
| `SPRINT_NAME` | Sprint to filter by | `Sprint 23`, or leave unset to use the active sprint |

## Security

⚠️ **Never commit your `.env` file!** It contains sensitive credentials.

The `.gitignore` file is configured to exclude `.env` automatically.

## Development

```bash
uv run pytest -q
```

The tests cover the offline helpers (time validation and formatting, and
which frequent tickets are offered). Nothing in the suite talks to Jira.

## License

MIT
