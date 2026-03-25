"""
Time Logging Controller - Business logic for time logging operations.
NO print statements - returns data structures for views to display.
"""
import os
from datetime import datetime, timedelta
from collections import defaultdict
from jira_lib.jira_api import get_issues_by_status, transition_issue
from jira_lib.jira_worklog import (
    get_worklogs_for_date_range,
    get_all_worklogs_for_date_range,
    seconds_to_hours
)
from config import get_frequent_tickets


class TimeController:
    """Controller for time logging operations."""

    def __init__(self, jira, sprint_name=None):
        self.jira = jira
        self.sprint_name = sprint_name
        self.jira_url = os.getenv('JIRA_URL', 'https://your-domain.atlassian.net')

    def get_frequent_tickets(self):
        """Get frequent tickets from config."""
        return get_frequent_tickets()
    
    def get_in_progress_tickets(self):
        """
        Get list of in progress tickets.
        Returns: (success: bool, tickets: list or error: Exception)
        """
        try:
            issues = get_issues_by_status(self.jira, self.sprint_name, 'In Progress')
            return (True, issues)
        except Exception as e:
            return (False, e)
    
    def validate_ticket(self, ticket_key):
        """
        Validate and fetch ticket details.
        Returns: (success: bool, issue or error: Exception)
        """
        try:
            issue = self.jira.issue(ticket_key)
            return (True, issue)
        except Exception as e:
            return (False, e)
    
    def validate_time_format(self, time_input):
        """
        Validate time input format matches Jira's expected format.
        Args:
            time_input: Time string (e.g., '2h', '30m', '1h 30m')
        Returns: (valid: bool, error_message: str or None)
        """
        import re
        
        # Jira accepts: 1w, 2d, 3h, 4m (weeks, days, hours, minutes)
        # Can be combined: 1h 30m, 2d 4h, etc.
        pattern = r'^(\d+(\.\d+)?[wdhm]\s*)+$'
        
        if not time_input or not time_input.strip():
            return (False, "Time cannot be empty")
        
        time_input = time_input.strip().lower()
        
        if not re.match(pattern, time_input):
            return (False, "Invalid format. Use Jira time format: '2h', '30m', '1h 30m', '2d 4h', etc.")
        
        return (True, None)
    
    def parse_start_time(self, start_time_input):
        """
        Parse start time input (e.g., '2:30pm', '14:30').
        Returns: (success: bool, datetime or None)
        """
        if not start_time_input:
            return (True, None)
        
        try:
            # Try parsing common time formats
            for fmt in ['%I:%M%p', '%I:%M %p', '%H:%M']:
                try:
                    time_obj = datetime.strptime(start_time_input.strip(), fmt)
                    today = datetime.now().date()
                    started_datetime = datetime.combine(today, time_obj.time())
                    return (True, started_datetime)
                except ValueError:
                    continue
            return (False, None)
        except Exception as e:
            return (False, None)
    
    def log_worklog(self, worklog_func, ticket_key, time_spent, comment=None, started_datetime=None):
        """
        Log work to a ticket.
        Args:
            time_spent: Time string in Jira format (e.g., '2h', '30m', '1h 30m')
        Returns: (success: bool, error: Exception or None)
        """
        try:
            worklog_func(self.jira, ticket_key, time_spent, comment, started=started_datetime)
            return (True, None)
        except Exception as e:
            return (False, e)
    
    def close_ticket_if_done(self, ticket_key):
        """
        Attempt to close a ticket marked as done.
        Returns: (success: bool)
        """
        success, _ = transition_issue(self.jira, ticket_key, 'Closed')
        return success
    
    def get_weekly_summary(self, user_email, all_tickets=False):
        """
        Get weekly time summary data.
        Returns: dict with {
            'start_date': datetime,
            'end_date': datetime,
            'logs_by_day': {date_str: [log_dict, ...]},
            'total_by_day': {date_str: seconds},
            'grand_total': seconds,
            'all_tickets': bool
        }
        """
        # Get Monday of current week
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Get worklogs
        if all_tickets:
            worklogs = get_all_worklogs_for_date_range(self.jira, user_email, start_date, end_date)
        else:
            worklogs = get_worklogs_for_date_range(self.jira, self.sprint_name, user_email, start_date, end_date)
        
        # Group by day
        logs_by_day = defaultdict(list)
        total_by_day = defaultdict(int)
        
        for issue_key, issue_summary, worklog in worklogs:
            worklog_date = datetime.strptime(worklog.started[:10], '%Y-%m-%d')
            date_str = worklog_date.strftime('%A, %B %d')  # "Monday, January 15"
            
            log_entry = {
                'issue_key': issue_key,
                'issue_summary': issue_summary,
                'time_spent': worklog.timeSpentSeconds,
                'comment': getattr(worklog, 'comment', '')
            }
            
            logs_by_day[date_str].append(log_entry)
            total_by_day[date_str] += worklog.timeSpentSeconds
        
        grand_total = sum(total_by_day.values())
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'logs_by_day': dict(logs_by_day),
            'total_by_day': dict(total_by_day),
            'grand_total': grand_total,
            'all_tickets': all_tickets
        }
    
    def get_time_by_ticket(self, user_email, status_filter=None):
        """
        Get time logged grouped by ticket.
        Returns: dict with {
            'start_date': datetime,
            'end_date': datetime,
            'tickets': {issue_key: {'summary': str, 'status': str, 'total_time': seconds, 'logs': [log_dict, ...]}},
            'grand_total': seconds,
            'status_filter': str or None
        }
        """
        # Get Monday of current week
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Get worklogs for sprint tickets
        worklogs = get_worklogs_for_date_range(self.jira, self.sprint_name, user_email, start_date, end_date)
        
        # Group by ticket
        time_by_ticket = defaultdict(lambda: {
            'summary': '',
            'status': '',
            'total_time': 0,
            'logs': []
        })
        
        for issue_key, issue_summary, worklog in worklogs:
            # Get status for this issue
            if not time_by_ticket[issue_key]['summary']:
                try:
                    issue = self.jira.issue(issue_key)
                    time_by_ticket[issue_key]['summary'] = issue_summary
                    time_by_ticket[issue_key]['status'] = issue.fields.status.name
                except Exception:
                    time_by_ticket[issue_key]['summary'] = issue_summary
                    time_by_ticket[issue_key]['status'] = 'Unknown'
            
            time_by_ticket[issue_key]['total_time'] += worklog.timeSpentSeconds  # type: ignore
            
            worklog_date = datetime.strptime(worklog.started[:10], '%Y-%m-%d')
            log_entry = {
                'date': worklog_date.strftime('%A, %B %d'),
                'time_spent': worklog.timeSpentSeconds,
                'comment': getattr(worklog, 'comment', '')
            }
            time_by_ticket[issue_key]['logs'].append(log_entry)  # type: ignore
        
        # Filter by status if requested
        if status_filter:
            time_by_ticket = {
                k: v for k, v in time_by_ticket.items() 
                if v['status'] == status_filter
            }
        
        # Sort by total time (descending)
        sorted_tickets = dict(sorted(
            time_by_ticket.items(),
            key=lambda x: x[1]['total_time'],  # type: ignore
            reverse=True
        ))
        
        grand_total = sum(ticket['total_time'] for ticket in sorted_tickets.values())  # type: ignore
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'tickets': sorted_tickets,
            'grand_total': grand_total,
            'status_filter': status_filter
        }

