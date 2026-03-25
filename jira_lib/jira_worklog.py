"""
Functions for working with Jira work logs (time tracking).
"""
from datetime import datetime, timedelta


def get_worklog_for_issue(jira, issue_key):
    """
    Get all work logs for a specific issue.
    
    Args:
        jira: JIRA client instance
        issue_key: Issue key (e.g., 'PROJECT-1234')
    """
    try:
        issue = jira.issue(issue_key, fields='worklog')
        return issue.fields.worklog.worklogs
    except Exception as e:
        print(f"[WARN] Warning: Could not get worklogs for {issue_key}: {e}")
        return []


def get_my_worklogs_for_sprint(jira, sprint_name, current_user_email):
    """
    Get all work logs by current user for tickets in a specific sprint.
    
    Args:
        jira: JIRA client instance
        sprint_name: Sprint name to filter by
        current_user_email: Email of current user to filter work logs
        
    Returns:
        List of tuples: (issue_key, issue_summary, worklog_entry)
    """
    # Get all issues in the sprint assigned to current user
    if sprint_name:
        jql = f'assignee = currentUser() AND sprint = "{sprint_name}"'
    else:
        jql = 'assignee = currentUser() AND sprint in openSprints()'
    
    issues = jira.search_issues(jql, maxResults=100, fields='summary,worklog')
    
    my_worklogs = []
    for issue in issues:
        if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
            for worklog in issue.fields.worklog.worklogs:
                # Filter to only current user's work logs
                if hasattr(worklog, 'author') and worklog.author.emailAddress == current_user_email:
                    my_worklogs.append((issue.key, issue.fields.summary, worklog))
    
    return my_worklogs


def get_all_my_worklogs(jira, current_user_email):
    """
    Get all work logs by current user across ALL tickets (not sprint-filtered).
    
    Args:
        jira: JIRA client instance
        current_user_email: Email of current user to filter work logs
        
    Returns:
        List of tuples: (issue_key, issue_summary, worklog_entry)
    """
    # Get all issues where current user has logged time (not just assigned tickets)
    jql = 'worklogAuthor = currentUser()'
    
    issues = jira.search_issues(jql, maxResults=150, fields='summary,worklog')
    
    my_worklogs = []
    for issue in issues:
        if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
            for worklog in issue.fields.worklog.worklogs:
                # Filter to only current user's work logs
                if hasattr(worklog, 'author') and worklog.author.emailAddress == current_user_email:
                    my_worklogs.append((issue.key, issue.fields.summary, worklog))
    
    return my_worklogs


def get_worklogs_for_date_range(jira, sprint_name, current_user_email, start_date, end_date):
    """
    Get work logs within a date range.
    
    Args:
        jira: JIRA client instance
        sprint_name: Sprint name to filter by
        current_user_email: Email of current user
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        
    Returns:
        List of tuples: (issue_key, issue_summary, worklog_entry)
    """
    all_worklogs = get_my_worklogs_for_sprint(jira, sprint_name, current_user_email)
    
    filtered_worklogs = []
    for issue_key, issue_summary, worklog in all_worklogs:
        # Parse worklog started date
        worklog_date = datetime.strptime(worklog.started[:10], '%Y-%m-%d')
        
        # Compare dates only (normalize to date comparison)
        if start_date.date() <= worklog_date.date() <= end_date.date():
            filtered_worklogs.append((issue_key, issue_summary, worklog))
    
    return filtered_worklogs


def get_all_worklogs_for_date_range(jira, current_user_email, start_date, end_date):
    """
    Get work logs within a date range for ALL tickets (not sprint-filtered).
    Uses JQL worklogDate to find tickets where you logged time in the date range.
    
    Args:
        jira: JIRA client instance
        current_user_email: Email of current user
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        
    Returns:
        List of tuples: (issue_key, issue_summary, worklog_entry)
    """
    # Use JQL to find issues where current user logged time in the date range
    # This searches across ALL projects and tickets, not just assigned ones
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    jql = f'worklogAuthor = currentUser() AND worklogDate >= "{start_str}" AND worklogDate <= "{end_str}"'
    
    issues = jira.search_issues(jql, maxResults=150, fields='summary,worklog')
    
    my_worklogs = []
    for issue in issues:
        if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
            # Get ALL worklogs for this issue (may need pagination)
            all_worklogs = jira.worklogs(issue.key)
            
            for worklog in all_worklogs:
                # Filter to only current user's work logs in the date range
                if hasattr(worklog, 'author') and worklog.author.emailAddress == current_user_email:
                    worklog_date = datetime.strptime(worklog.started[:10], '%Y-%m-%d')
                    
                    # Compare dates only (normalize to date comparison)
                    if start_date.date() <= worklog_date.date() <= end_date.date():
                        my_worklogs.append((issue.key, issue.fields.summary, worklog))
    
    return my_worklogs


def seconds_to_hours(seconds):
    """
    Convert seconds to hours (rounded to 2 decimal places).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Hours as float
    """
    return round(seconds / 3600, 2)


def format_worklog_time(seconds):
    """
    Format seconds into human-readable time (e.g., '2h 30m').
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


def add_worklog(jira, issue_key, time_spent, comment="", started=None):
    """
    Add a work log entry to an issue.
    
    Args:
        jira: JIRA client instance
        issue_key: Issue key (e.g., 'PROJECT-1234')
        comment: Optional comment/description of work done
        started: Optional datetime when work started (defaults to now)
        
    Returns:
        Created worklog object or None if failed
    """
    try:
        if started:
            jira.add_worklog(issue_key, timeSpent=time_spent, comment=comment, started=started)
        else:
            jira.add_worklog(issue_key, timeSpent=time_spent, comment=comment)
        return True
    except Exception as e:
        print(f"[ERROR] Could not add worklog to {issue_key}: {e}")
        return False
