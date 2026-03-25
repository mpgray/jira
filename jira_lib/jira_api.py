"""
Jira API wrapper functions for connecting and querying issues.
"""
from jira import JIRA


def connect_to_jira(url, email, api_token):
    """
    Connect to Jira with the given credentials.
    
    Args:
        url: Jira instance URL
        email: User email
        api_token: API token for authentication
        
    Returns:
        JIRA client instance
    """
    return JIRA(
        server=url,
        basic_auth=(email, api_token),
        options={'server': url, 'rest_api_version': 'latest'}
    )


def search_sprint_issues(jira, sprint_name=None):
    """
    Search for issues assigned to current user in a sprint.
    
    Args:
        jira: JIRA client instance
        sprint_name: Specific sprint name, or None for all open sprints
        
    Returns:
        List of issues
    """
    if sprint_name:
        jql = f'assignee = currentUser() AND sprint = "{sprint_name}"'
    else:
        jql = 'assignee = currentUser() AND sprint in openSprints()'
    
    return jira.search_issues(jql, maxResults=100)


def get_issues_by_status(jira, sprint_name, status):
    """
    Get issues with a specific status.
    
    Args:
        jira: JIRA client instance
        sprint_name: Sprint name to filter by
        status: Status name (e.g., 'Open', 'In Progress')
        
    Returns:
        List of issues
    """
    if sprint_name:
        jql = f'assignee = currentUser() AND status = "{status}" AND sprint = "{sprint_name}"'
    else:
        jql = f'assignee = currentUser() AND status = "{status}" AND sprint in openSprints()'
    
    return jira.search_issues(jql, maxResults=100)


def get_active_sprint(jira):
    """
    Get the currently active sprint for the user.
    
    Args:
        jira: JIRA client instance
        
    Returns:
        Sprint name string or None if no active sprint found
    """
    try:
        # Get issues in open sprints - don't limit fields so we get the sprint custom field
        jql = 'assignee = currentUser() AND sprint in openSprints()'
        issues = jira.search_issues(jql, maxResults=1)
        
        if issues:
            # Get the first issue and extract sprint info
            issue = issues[0]
            # Sprint is stored in customfield - need to find it
            for field_name, field_value in issue.raw['fields'].items():
                if field_value and isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, dict) and 'name' in item and item.get('state') == 'active':
                            return item['name']
        
        return None
    except Exception as e:
        print(f"[WARN] Warning: Could not get active sprint: {e}")
        return None


def get_project_statuses(jira, project_key=None):
    """
    Get all available statuses from Jira.
    
    Args:
        jira: JIRA client instance
        project_key: Optional project key to get project-specific statuses
        
    Returns:
        List of status names
    """
    try:
        if project_key:
            # Get statuses for a specific project
            project = jira.project(project_key)
            statuses = jira.statuses()
        else:
            # Get all statuses by checking current user's tickets
            jql = 'assignee = currentUser() ORDER BY updated DESC'
            issues = jira.search_issues(jql, maxResults=100)
            status_set = set()
            for issue in issues:
                status_set.add(issue.fields.status.name)
            return sorted(status_set)
    except Exception as e:
        print(f"[WARN] Warning: Could not get statuses: {e}")
        return []


def find_ticket_with_comment(jira, issues, comment_text):
    """
    Find a ticket that has a specific comment from the current user.
    
    Args:
        jira: JIRA client instance
        issues: List of issues to search through
        comment_text: The comment text to search for
        
    Returns:
        Issue object if found, None otherwise
    """
    try:
        for issue in issues:
            # Get comments for this issue
            comments = jira.comments(issue.key)
            for comment in comments:
                # Check if comment is from current user and contains the text
                if comment_text.lower() in comment.body.lower():
                    return issue
        return None
    except Exception as e:
        print(f"[WARN] Warning: Could not search comments: {e}")
        return None


def transition_issue(jira, issue_key, transition_name, comment=None):
    """
    Transition an issue to a new status.

    Args:
        jira: JIRA client instance
        issue_key: Issue key (e.g., 'PROJECT-1234')
        transition_name: Target status name (e.g., 'In Progress', 'Closed')
        comment: Optional comment to add after transitioning

    Returns:
        (success: bool, error: str or None)
    """
    try:
        transitions = jira.transitions(issue_key)
        transition_id = next(
            (t['id'] for t in transitions if t['name'].lower() == transition_name.lower()),
            None,
        )
        if not transition_id:
            return (False, f"Transition '{transition_name}' not available")
        jira.transition_issue(issue_key, transition_id)
        if comment:
            jira.add_comment(issue_key, comment)
        return (True, None)
    except Exception as e:
        return (False, str(e))
