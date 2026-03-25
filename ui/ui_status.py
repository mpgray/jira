"""
Ticket Status View - Handles all display logic for ticket status viewing.
"""
import os
from ui.ui_utils import Colors, colorize, make_ticket_link, format_time_display


class StatusView:
    """View layer for ticket status operations."""
    
    def __init__(self, jira_url=None):
        self.jira_url = jira_url or os.getenv('JIRA_URL', 'https://your-domain.atlassian.net')
    
    def show_header(self, title="TICKET STATUS VIEW"):
        """Display header."""
        print(f"\n{Colors.CYAN}━━━ {title} ━━━{Colors.ENDC}\n")
    
    def show_sprint_name(self, sprint_name):
        """Display sprint name."""
        print(f"{Colors.BOLD}Sprint:{Colors.ENDC} {sprint_name}\n")
    
    def show_no_sprint_warning(self):
        """Display no sprint warning."""
        print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} No active sprint found - showing all open tickets\n")
    
    def show_ticket_count(self, count):
        """Display ticket count."""
        print(f"Found {Colors.BOLD}{count}{Colors.ENDC} total issues\n")
    
    def show_status_group(self, status, count):
        """Display status group header."""
        # Determine color based on status
        color_map = {
            'Open': Colors.BLUE,
            'In Queue': Colors.CYAN,
            'In Progress': Colors.YELLOW,
            'Pending Review': Colors.HEADER,
            'In Review': Colors.HEADER,
            'Awaiting Merge': Colors.GREEN,
            'Done': Colors.GREEN,
            'Closed': Colors.GREEN,
            'Canceled': Colors.RED,
            'On Hold': Colors.YELLOW,
            'Blocked': Colors.RED,
        }
        color = color_map.get(status, Colors.BOLD)
        
        print(f"\n{'='*80}")
        print(colorize(f"{status} ({count})", color + Colors.BOLD))
        print('='*80)
    
    def show_other_statuses_header(self):
        """Display other statuses header."""
        print(f"\n{'='*80}")
        print(colorize("Other Statuses", Colors.BOLD))
        print('='*80)
    
    def show_status_subgroup(self, status, count):
        """Display status subgroup."""
        print(f"\n{status} ({count})")
    
    def show_ticket(self, issue):
        """Display a ticket with optional time."""
        ticket_link = make_ticket_link(issue.key, self.jira_url)
        time_str = ""
        
        if hasattr(issue.fields, 'timespent') and issue.fields.timespent:
            time_display = format_time_display(issue.fields.timespent)
            time_str = f" [{time_display}]"
        
        print(f"  {colorize(ticket_link, Colors.BOLD)} | {issue.fields.summary}{colorize(time_str, Colors.GREEN)}")
    
    def show_status_total_time(self, status, time_seconds):
        """Display total time for status."""
        if time_seconds > 0:
            time_display = format_time_display(time_seconds)
            print(colorize(f"\n  Total time logged in {status}: {time_display}", Colors.GREEN + Colors.BOLD))
    
    def show_footer(self):
        """Display footer."""
        print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")
    
    def show_done(self):
        """Display completion message."""
        print("\nDone!")
