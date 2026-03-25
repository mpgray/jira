"""
Jira Library - Data access layer.
Pure data access functions with no display logic.
"""

from .jira_api import connect_to_jira, search_sprint_issues, get_issues_by_status, get_active_sprint, find_ticket_with_comment, transition_issue
from .session import JiraSession
from .jira_worklog import get_worklog_for_issue, get_my_worklogs_for_sprint, get_all_my_worklogs, seconds_to_hours, format_worklog_time, add_worklog

__all__ = [
    'JiraSession',
    'connect_to_jira',
    'search_sprint_issues',
    'get_issues_by_status',
    'get_active_sprint',
    'find_ticket_with_comment',
    'transition_issue',
    'get_worklog_for_issue',
    'get_my_worklogs_for_sprint',
    'get_all_my_worklogs',
    'seconds_to_hours',
    'format_worklog_time',
    'add_worklog',
]
