# Jira Automation Scripts

Python scripts for automating Jira ticket management and status tracking.

## Setup

1. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install jira python-dotenv
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your Jira credentials and settings
   - Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Scripts

### `ticket_status.py`
Displays all your tickets grouped by status for the current sprint.

**Usage:**
```bash
python ticket_status.py
```

**Output:**
- Shows tickets organized by status (Open, In Progress, In Queue, etc.)
- Displays count for each status
- Lists ticket keys and summaries

### `daily_ticket_updates.py`
Automates daily ticket management tasks.

**Features:**
1. Adds comments to all 'Open' tickets acknowledging them
2. Moves specified tickets to 'In Queue' with context about current work

**Usage:**
```bash
# Preview mode (shows what would happen without making changes)
python daily_ticket_updates.py

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

### Main Scripts
- `ticket_status.py` - View tickets by status
- `daily_ticket_updates.py` - Automate daily ticket updates

### Library Modules (in `jira_lib/` package)
- `jira_lib/jira_api.py` - Jira connection and querying functions
- `jira_lib/jira_actions.py` - Functions for modifying tickets (comments, transitions)
- `jira_lib/jira_display.py` - Display and formatting functions
- `jira_lib/ticket_workflows.py` - High-level workflow functions for daily updates
- `config.py` - Configuration loader for environment variables
- `jira_helpers.py` - *(Deprecated)* Backward compatibility wrapper

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
| `SPRINT_NAME` | Sprint to filter by | `Sprint 23` or leave empty for all open sprints |

## Security

⚠️ **Never commit your `.env` file!** It contains sensitive credentials.

The `.gitignore` file is configured to exclude `.env` automatically.
