import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_jira_config():
    """
    Get Jira configuration from environment variables.
    
    Returns:
        Dictionary containing Jira configuration
    """
    return {
        'url': os.getenv('JIRA_URL'),
        'email': os.getenv('JIRA_EMAIL'),
        'api_token': os.getenv('JIRA_API_TOKEN'),
    }


def get_sprint_name(jira=None):
    """
    Get the sprint name from environment variables, or fetch active sprint if not set.
    
    Priority:
    1. SPRINT_NAME env var (if set and not 'current')
    2. Active sprint from Jira API (default)
    3. None (if no active sprint found)
    
    Args:
        jira: Optional JIRA client instance for fetching active sprint
    
    Returns:
        Sprint name string or None
    """
    sprint = os.getenv('SPRINT_NAME', 'current').strip()
    
    # If SPRINT_NAME is 'current' or empty, get active sprint from Jira
    if (not sprint or sprint.lower() == 'current') and jira:
        from jira_lib import get_active_sprint
        active = get_active_sprint(jira)
        if active:
            return active
        return None
    
    # If SPRINT_NAME is set to a specific value, use it
    return sprint if sprint else None


def get_frequent_tickets():
    """
    Get frequent time logging tickets from environment variables.
    Only includes tickets whose environment variable is set.

    Returns:
        Dictionary mapping shortcut keys to (ticket_key, name) tuples
    """
    candidates = [
        ("1", 'TICKET_STAND_UP', "Stand Up"),
        ("2", 'TICKET_SPRINT_PLANNING', "Sprint Planning"),
        ("3", 'TICKET_SPRINT_RETRO', "Sprint Retro"),
        ("4", 'TICKET_SPRINT_REFINEMENT', "Sprint Refinement"),
        ("5", 'TICKET_SPRINT_REVIEW', "Sprint Review"),
        ("6", 'TICKET_REGRESSION_REVIEW', "Regression Review"),
    ]
    return {
        key: (os.getenv(env_var), name)
        for key, env_var, name in candidates
        if os.getenv(env_var)
    }


def get_default_comments():
    """
    Get default comments for frequent tickets.
    Only includes entries where the ticket env var is set.

    Returns:
        Dictionary mapping ticket keys to default comment strings
    """
    defaults = [
        ('TICKET_STAND_UP', "attend standup"),
        ('TICKET_SPRINT_PLANNING', "attend sprint planning"),
        ('TICKET_SPRINT_RETRO', "attend sprint retro"),
        ('TICKET_SPRINT_REFINEMENT', "attend sprint refinement"),
        ('TICKET_SPRINT_REVIEW', "prepare for, present, and attend sprint review"),
        ('TICKET_REGRESSION_REVIEW', "evaluate regression tests"),
    ]
    return {
        os.getenv(env_var): comment
        for env_var, comment in defaults
        if os.getenv(env_var)
    }

