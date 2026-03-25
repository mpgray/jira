"""
Workflow Controller - Business logic for ticket workflow operations.
NO print statements - returns data structures for views to display.
"""
from jira_lib.jira_api import get_issues_by_status, transition_issue


class WorkflowController:
    """Controller for ticket workflow operations."""

    def __init__(self, jira, sprint_name):
        self.jira = jira
        self.sprint_name = sprint_name

    def get_tickets_by_status(self, status):
        """
        Get tickets in a specific status.
        Returns: List of issues
        """
        # get_issues_by_status handles None sprint_name properly
        return get_issues_by_status(self.jira, self.sprint_name, status)
    
    def get_open_tickets(self):
        """Get all open tickets."""
        return self.get_tickets_by_status('Open')
    
    def get_queue_tickets(self):
        """Get all in queue tickets."""
        return self.get_tickets_by_status('In Queue')
    
    def get_in_progress_tickets(self):
        """Get all in progress tickets."""
        return self.get_tickets_by_status('In Progress')
    
    def check_pr_links(self, issue):
        """
        Check if issue has PR links in description or comments.
        Returns: (has_pr: bool, pr_url: str or None, is_merged: bool)
        """
        # Check description for PR links
        description = issue.fields.description or ""
        pr_url = None
        
        # Look for GitHub/Bitbucket/GitLab PR patterns
        import re
        pr_patterns = [
            r'https://github\.com/[^/]+/[^/]+/pull/\d+',
            r'https://bitbucket\.org/[^/]+/[^/]+/pull-requests/\d+',
            r'https://gitlab\.com/[^/]+/[^/]+/-/merge_requests/\d+',
        ]
        
        for pattern in pr_patterns:
            match = re.search(pattern, description)
            if match:
                pr_url = match.group(0)
                break
        
        if not pr_url:
            # Check comments
            try:
                comments = self.jira.comments(issue)
                for comment in comments:
                    for pattern in pr_patterns:
                        match = re.search(pattern, comment.body)
                        if match:
                            pr_url = match.group(0)
                            break
                    if pr_url:
                        break
            except Exception:
                pass
        
        if not pr_url:
            return (False, None, False)
        
        # Check if PR is merged (simplified - would need GitHub API for real check)
        # For now, just check if "merged" or "closed" appears near the PR link
        is_merged = "merged" in description.lower() or "closed" in description.lower()
        
        return (True, pr_url, is_merged)
    
    def transition_ticket(self, issue_key, target_status, comment=None):
        """
        Transition a ticket to a new status.
        Returns: (success: bool, error: str or None)
        """
        return transition_issue(self.jira, issue_key, target_status, comment)

    def add_comment(self, issue_key, comment):
        """
        Add comment to a ticket.
        Returns: (success: bool, error: str or None)
        """
        try:
            self.jira.add_comment(issue_key, comment)
            return (True, None)
        except Exception as e:
            return (False, str(e))
    
    def get_priority_value(self, issue):
        """
        Get numeric priority value for sorting.
        Returns: int (lower is higher priority)
        """
        priority_map = {
            'Highest': 1,
            'High': 2,
            'Medium': 3,
            'Low': 4,
            'Lowest': 5,
        }
        
        if hasattr(issue.fields, 'priority') and issue.fields.priority:
            return priority_map.get(issue.fields.priority.name, 99)
        return 99
    
    def process_tickets_with_prs(self, dry_run=True, pending_comment=None, closed_comment=None):
        """
        Process in progress tickets that have PR links.
        Returns: list of dicts with ticket info and actions taken
        """
        tickets = self.get_in_progress_tickets()
        results = []
        
        for issue in tickets:
            has_pr, pr_url, is_merged = self.check_pr_links(issue)
            
            if has_pr:
                result = {
                    'issue_key': issue.key,
                    'summary': issue.fields.summary,
                    'pr_url': pr_url,
                    'is_merged': is_merged,
                    'action': None,
                    'success': None,
                    'error': None
                }
                
                if not dry_run:
                    if is_merged:
                        # Transition to Closed
                        success, error = self.transition_ticket(issue.key, 'Closed', closed_comment)
                        result['action'] = 'close'
                        result['success'] = success
                        result['error'] = error
                    else:
                        # Transition to Pending Review
                        success, error = self.transition_ticket(issue.key, 'Pending Review', pending_comment)
                        result['action'] = 'pending_review'
                        result['success'] = success
                        result['error'] = error
                else:
                    # Dry run - just record what would happen
                    result['action'] = 'close' if is_merged else 'pending_review'
                    result['success'] = True
                
                results.append(result)
        
        return results
    
    def move_tickets_to_queue(self, ticket_keys, comment=None, dry_run=True):
        """
        Move specified tickets to In Queue status.
        Returns: list of dicts with results for each ticket
        """
        results = []
        
        for ticket_key in ticket_keys:
            try:
                issue = self.jira.issue(ticket_key)
                result = {
                    'issue_key': ticket_key,
                    'summary': issue.fields.summary,
                    'success': None,
                    'error': None
                }
                
                if not dry_run:
                    success, error = self.transition_ticket(ticket_key, 'In Queue', comment)
                    result['success'] = success
                    result['error'] = error
                else:
                    result['success'] = True
                
                results.append(result)
            except Exception as e:
                results.append({
                    'issue_key': ticket_key,
                    'summary': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def move_queue_to_progress(self, comment=None, dry_run=True):
        """
        Move all In Queue tickets to In Progress.
        Returns: list of dicts with results for each ticket
        """
        queue_issues = self.get_queue_tickets()
        results = []
        
        for issue in queue_issues:
            result = {
                'issue_key': issue.key,
                'summary': issue.fields.summary,
                'success': None,
                'error': None
            }
            
            if not dry_run:
                success, error = self.transition_ticket(issue.key, 'In Progress', comment)
                result['success'] = success
                result['error'] = error
            else:
                result['success'] = True
            
            results.append(result)
        
        return results
