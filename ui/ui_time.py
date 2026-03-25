"""
Time Logging View - Handles all display logic for time logging operations.
"""
import os
from jira_lib.jira_worklog import format_worklog_time, seconds_to_hours
from ui.ui_utils import Colors, colorize, make_ticket_link, print_header, print_separator


class TimeView:
    """View layer for time logging operations."""

    def show_header(self):
        """Display time logging header."""
        print_header("LOG TIME TO TICKET")
        timesheet_url = os.getenv('JIRA_TIMESHEET_URL')
        if timesheet_url:
            print(f"\n{Colors.CYAN}Timesheet: {timesheet_url}{Colors.ENDC}\n")
    
    def show_frequent_tickets(self, frequent_tickets, jira_url):
        """Display frequent ticket options."""
        print("\nFREQUENT TICKETS:")
        for key, (ticket_key, name) in frequent_tickets.items():
            ticket_link = make_ticket_link(ticket_key, jira_url)
            print(f"  {key}. {name} ({ticket_link})")
    
    def show_in_progress_tickets(self, issues, jira_url):
        """Display in progress ticket options."""
        print("\nIN PROGRESS TICKETS:")
        if issues:
            for idx, issue in enumerate(issues, 1):
                ticket_link = make_ticket_link(issue.key, jira_url)
                print(f"  {idx}. {ticket_link}: {issue.fields.summary}")
        else:
            print("  (No In Progress tickets)")
    
    def show_in_progress_error(self, error):
        """Show error loading in progress tickets."""
        print(f"  (Could not load In Progress tickets: {str(error)})")
    
    def show_manual_entry_prompt(self):
        """Show prompt for manual ticket entry."""
        print("\nOr enter ticket key manually")
        print("-" * 80)
    
    def show_selected_ticket(self, ticket_key, ticket_name):
        """Display selected ticket."""
        print(f"Selected: {ticket_name}")
    
    def show_ticket_details(self, issue):
        """Display ticket details."""
        print(f"\nTicket: {issue.key} - {issue.fields.summary}")
        print(f"Status: {issue.fields.status.name}\n")
    
    def show_ticket_error(self, ticket_key, error):
        """Display ticket not found error."""
        print(f"Error: Could not find ticket {ticket_key}")
        print(f"Details: {str(error)}")
    
    def show_default_comment(self, comment):
        """Display available default comment."""
        print(f"\nDefault comment available: \"{comment}\"")
    
    def show_using_default_comment(self):
        """Indicate using default comment."""
        print("[OK] Using default comment")
    
    def show_time_format_error(self, error_message):
        """Show time format validation error."""
        print(f"\n{Colors.RED}[ERROR] {error_message}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Examples: '2h', '30m', '1h 30m', '2d 4h'{Colors.ENDC}\n")
    
    def show_time_parse_warning(self, time_input):
        """Show warning about time parsing."""
        print(f"  [WARN] Could not parse time '{time_input}', using current time instead")

    def show_time_parse_error(self, error):
        """Show error parsing time."""
        print(f"  [WARN] Error parsing start time: {str(error)}, using current time instead")
        """Display summary before logging."""
        print("\nReady to log:")
        print(f"  Ticket: {ticket_key}")
        print(f"  Time: {time_input}")
        if started_datetime:
            print(f"  Started: {started_datetime.strftime('%I:%M %p')}")
        if comment_input:
            print(f"  Comment: {comment_input}")
    
    def show_log_success(self, ticket_key):
        """Display success message."""
        print(f"\n[OK] Time logged successfully to {ticket_key}")

    def show_close_success(self, ticket_key):
        """Display ticket closed message."""
        print(f"[OK] Ticket {ticket_key} closed successfully")

    def show_close_warning(self, ticket_key):
        """Display warning that ticket couldn't be closed."""
        print(f"[WARN] Could not close ticket {ticket_key} - may need to be done manually")
        """Display logging error."""
        print(f"\n[ERROR] Error logging time: {str(error)}")
    
    def show_cancelled(self):
        """Display cancellation message."""
        print("\nCancelled.")
    
    def show_comment_warning(self, error):
        """Display comment add warning."""
        print(f"  [WARN] Warning: Could not add comment: {str(error)}")

    def show_transition_unavailable(self, issue_key, transition_name, available_transitions):
        """Display transition not available."""
        print(f"  [WARN] Transition '{transition_name}' not available for {issue_key}")
        print(f"      Available transitions: {[t['name'] for t in available_transitions]}")

    def show_transition_error(self, issue_key, error):
        """Display transition error."""
        print(f"  [ERROR] Error transitioning {issue_key}: {str(error)}")
        """Display weekly time summary."""
        start_date = summary_data['start_date']
        end_date = summary_data['end_date']
        all_tickets = summary_data['all_tickets']
        
        # Header
        title = f"TIME LOG SUMMARY{' (ALL TICKETS)' if all_tickets else ''}: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        timesheet_url = os.getenv('JIRA_TIMESHEET_URL')
        if timesheet_url:
            print(f"{Colors.CYAN}Timesheet: {timesheet_url}{Colors.ENDC}")
        print("=" * 80)
        
        if not summary_data['logs_by_day']:
            print("\nNo time logged this week.")
            return
        
        # Display by day
        for date_str in sorted(summary_data['logs_by_day'].keys()):
            logs = summary_data['logs_by_day'][date_str]
            day_total = summary_data['total_by_day'][date_str]
            
            print(f"\n{Colors.CYAN}{date_str}{Colors.ENDC}")
            print("-" * 80)
            
            for log in logs:
                ticket_link = make_ticket_link(log['issue_key'], jira_url)
                time_str = format_worklog_time(log['time_spent'])
                print(f"  {colorize(log['issue_key'], Colors.BOLD)}: {log['issue_summary']}")
                print(f"    Time: {colorize(time_str, Colors.GREEN)}")
                if log['comment']:
                    print(f"    Comment: {log['comment']}")
            
            day_total_str = format_worklog_time(day_total)
            print(f"\n  {Colors.BOLD}Day Total: {colorize(day_total_str, Colors.GREEN)}{Colors.ENDC}")
        
        # Grand total
        grand_total_str = format_worklog_time(summary_data['grand_total'])
        grand_total_hours = seconds_to_hours(summary_data['grand_total'])
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}WEEK TOTAL: {colorize(grand_total_str, Colors.GREEN)} ({grand_total_hours}h){Colors.ENDC}\n")
    
    def show_time_by_ticket(self, time_data, jira_url):
        """Display time logged grouped by ticket."""
        start_date = time_data['start_date']
        end_date = time_data['end_date']
        status_filter = time_data['status_filter']
        
        # Header
        title = f"TIME BY TICKET{' (' + status_filter + ' only)' if status_filter else ''}: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        timesheet_url = os.getenv('JIRA_TIMESHEET_URL')
        if timesheet_url:
            print(f"{Colors.CYAN}Timesheet: {timesheet_url}{Colors.ENDC}")
        print("=" * 80)
        
        if not time_data['tickets']:
            print(f"\nNo time logged{' for ' + status_filter + ' tickets' if status_filter else ''} this week.")
            return
        
        # Display each ticket
        for issue_key, ticket_info in time_data['tickets'].items():
            ticket_link = make_ticket_link(issue_key, jira_url)
            total_time_str = format_worklog_time(ticket_info['total_time'])
            total_hours = seconds_to_hours(ticket_info['total_time'])
            
            print(f"\n{Colors.BOLD}{issue_key}{Colors.ENDC}: {ticket_info['summary']}")
            print(f"  Status: {colorize(ticket_info['status'], Colors.CYAN)}")
            print(f"  Total: {colorize(total_time_str, Colors.GREEN)} ({total_hours}h)")
            print("  " + "-" * 78)
            
            for log in ticket_info['logs']:
                time_str = format_worklog_time(log['time_spent'])
                print(f"    {log['date']}: {time_str}")
                if log['comment']:
                    print(f"      → {log['comment']}")
        
        # Grand total
        grand_total_str = format_worklog_time(time_data['grand_total'])
        grand_total_hours = seconds_to_hours(time_data['grand_total'])
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}TOTAL: {colorize(grand_total_str, Colors.GREEN)} ({grand_total_hours}h){Colors.ENDC}\n")
