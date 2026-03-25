"""
Session management for Jira connections and configuration.
Provides a centralized way to manage Jira connections, config, and user context.
"""
from .jira_api import connect_to_jira, get_active_sprint
from config import get_jira_config, get_sprint_name


class JiraSession:
    """
    Manages Jira connection and session context.
    
    Provides centralized access to:
    - Jira client instance
    - Configuration (URL, email, API token)
    - Sprint information
    - User information
    """
    
    def __init__(self):
        """Initialize session by loading config and connecting to Jira."""
        self.config = get_jira_config()
        self.jira = connect_to_jira(
            self.config['url'],
            self.config['email'],
            self.config['api_token']
        )
        self.sprint_name = get_sprint_name(self.jira)
        self.user_email = self.config['email']
        self.jira_url = self.config['url']
    
    def reconnect(self):
        """Reconnect to Jira (useful if connection is lost)."""
        self.jira = connect_to_jira(
            self.config['url'],
            self.config['email'],
            self.config['api_token']
        )
    
    def refresh_sprint(self):
        """Refresh the current sprint information."""
        self.sprint_name = get_sprint_name(self.jira)
        return self.sprint_name
    
    def __repr__(self):
        return f"JiraSession(url={self.config['url']}, sprint={self.sprint_name})"
