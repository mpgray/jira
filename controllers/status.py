"""
Ticket Status Controller - Business logic for viewing ticket status.
NO print statements - returns data structures for views to display.
"""
from jira_lib.jira_api import search_sprint_issues, get_project_statuses


class StatusController:
    """Controller for ticket status operations."""
    
    def __init__(self, jira, sprint_name=None, user_email=None):
        self.jira = jira
        self.sprint_name = sprint_name
        self.user_email = user_email
        self._cached_statuses = None
    
    def get_tickets(self):
        """
        Get all tickets for current user in the sprint.
        Returns: List of issues
        """
        # search_sprint_issues handles None properly
        return search_sprint_issues(self.jira, self.sprint_name)
    
    def group_by_status(self, issues):
        """
        Group issues by their status.
        Returns: dict of {status_name: [issues]}
        """
        grouped = {}
        for issue in issues:
            status = issue.fields.status.name
            if status not in grouped:
                grouped[status] = []
            grouped[status].append(issue)
        return grouped
    
    def get_status_order(self):
        """
        Get the standard order for displaying statuses.
        Fetches from actual Jira statuses, with fallback to common workflow order.
        Returns: list of status names
        """
        if self._cached_statuses is None:
            self._cached_statuses = get_project_statuses(self.jira)
        
        # If we got statuses from Jira, use them
        if self._cached_statuses:
            # Define preferred order for common statuses
            preferred_order = ['Open', 'In Queue', 'In Progress', 'Pending Review', 
                             'In Review', 'Awaiting Merge', 'Done', 'Closed', 
                             'Canceled', 'On Hold', 'Blocked']
            
            # Sort actual statuses by preferred order, then alphabetically
            def sort_key(status):
                try:
                    return (0, preferred_order.index(status))
                except ValueError:
                    return (1, status)
            
            return sorted(self._cached_statuses, key=sort_key)
        
        # Fallback to default order
        return ['Open', 'In Queue', 'In Progress', 'Pending Review', 'In Review', 
                'Awaiting Merge', 'Done', 'Closed', 'Canceled', 'On Hold', 'Blocked']
    
    def get_primary_statuses(self):
        """Get list of primary statuses to highlight."""
        # Active work statuses that should be highlighted
        return ['Open', 'In Queue', 'In Progress', 'Pending Review', 'In Review', 'Awaiting Merge', 'Done']
    
    def calculate_status_totals(self, issues):
        """
        Calculate total time logged for each status.
        Returns: dict of {status_name: total_seconds}
        """
        totals = {}
        for issue in issues:
            status = issue.fields.status.name
            time_seconds = issue.fields.timespent or 0
            totals[status] = totals.get(status, 0) + time_seconds
        return totals
