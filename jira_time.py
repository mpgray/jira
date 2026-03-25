#!/usr/bin/env python3
"""
Log Time - Time logging interface using MVC pattern.
Coordinates between Controller (business logic) and View (display).
"""

import sys
from typing import cast
from jira import Issue
from jira_lib import JiraSession
from jira_lib.jira_worklog import add_worklog
from ui import Menu, Colors
from controllers.time import TimeController
from ui.ui_time import TimeView
from config import get_default_comments


def log_time_interactive(session):
    """
    Interactive time logging using MVC pattern.
    Main script coordinates between Controller and View.
    """
    # Initialize controller and view
    controller = TimeController(session.jira, session.sprint_name)
    view = TimeView()
    
    # Display header
    view.show_header()
    
    # Get and display frequent tickets
    frequent_tickets = controller.get_frequent_tickets()
    if frequent_tickets:
        view.show_frequent_tickets(frequent_tickets, controller.jira_url)
    
        # Get in progress tickets
    tickets_success, tickets_result = controller.get_in_progress_tickets()
    
    if tickets_success:
        in_progress_tickets = tickets_result  # type: ignore - tickets_result is a list when success=True
        view.show_in_progress_tickets(in_progress_tickets, controller.jira_url)
    else:
        in_progress_tickets = []
        view.show_in_progress_error(tickets_result)  # type: ignore - tickets_result is error string when success=False
    
    # Show manual entry prompt
    view.show_manual_entry_prompt()
    
    # Get ticket selection
    ticket_input = input("Select ticket (number/key): ").strip()
    if not ticket_input:
        view.show_cancelled()
        return
    
    # Determine ticket key
    ticket_key = None
    ticket_name = None
    
    # Check if it's a frequent ticket number
    if ticket_input in frequent_tickets:
        ticket_key, ticket_name = frequent_tickets[ticket_input]
        view.show_selected_ticket(ticket_key, ticket_name)
    # Check if it's an in progress ticket number
    elif ticket_input.isdigit() and tickets_success:
        idx = int(ticket_input) - 1
        if 0 <= idx < len(in_progress_tickets):  # type: ignore
            issue = in_progress_tickets[idx]  # type: ignore
            ticket_key = issue.key
            ticket_name = issue.fields.summary
        else:
            view.show_cancelled()
            return
    # Assume it's a manual ticket key
    else:
        ticket_key = ticket_input.upper()
    
    # Validate ticket
    success, issue_result = controller.validate_ticket(ticket_key)
    if success:
        issue = cast(Issue, issue_result)  # Type assertion - we know it's an Issue when success=True
        view.show_ticket_details(issue)
    else:
        view.show_ticket_error(ticket_key, issue_result)
        return
    
    # Get time input
    time_input = input("Time spent (e.g., '2h', '30m', '1h 30m'): ").strip()
    if not time_input:
        view.show_cancelled()
        return
    
    # Validate time format
    valid, error_message = controller.validate_time_format(time_input)
    if not valid:
        view.show_time_format_error(error_message)
        return
    
    # Get comment
    default_comments = get_default_comments()
    default_comment = default_comments.get(ticket_key)
    
    if default_comment:
        view.show_default_comment(default_comment)
    
    comment_input = input("Comment (press Enter for default, or type comment): ").strip()
    
    if not comment_input and default_comment:
        comment_input = default_comment
        view.show_using_default_comment()
    
    # Get start time
    start_time_input = input("Start time (optional, e.g., '2:30pm'): ").strip()
    started_datetime = None
    
    if start_time_input:
        success, started_datetime = controller.parse_start_time(start_time_input)
        if not success:
            view.show_time_parse_warning(start_time_input)
    
    # Show summary
    view.show_log_summary(ticket_key, time_input, started_datetime, comment_input)
    
    # Confirm
    confirm = input("\nLog this time? (y/n): ").strip().lower()
    if confirm == 'y':
        # Log the time - pass time_input string directly
        success, error = controller.log_worklog(add_worklog, ticket_key, time_input, 
                                               comment_input, started_datetime)
        
        if success:
            view.show_log_success(ticket_key)
            
            # Only ask about closing if ticket is In Progress, in current sprint, and assigned to me
            should_prompt_close = (
                issue.fields.status.name == 'In Progress' and
                issue.fields.assignee and
                issue.fields.assignee.emailAddress == session.user_email
            )
            
            if should_prompt_close:
                # Check if in current sprint
                in_current_sprint = False
                if hasattr(issue.fields, 'customfield_10020'):  # Sprint field
                    sprint_field = issue.fields.customfield_10020
                    if sprint_field:
                        for sprint_data in sprint_field:
                            if isinstance(sprint_data, dict) and sprint_data.get('state') == 'active':
                                in_current_sprint = True
                                break
                
                if in_current_sprint:
                    done = input("\nIs this ticket done? Close it? (y/n): ").strip().lower()
                    if done == 'y':
                        if controller.close_ticket_if_done(ticket_key):
                            view.show_close_success(ticket_key)
                        else:
                            view.show_close_warning(ticket_key)
        else:
            view.show_log_error(error)
    else:
        view.show_cancelled()


def view_weekly_summary(session, all_tickets=False):
    """View weekly time summary."""
    controller = TimeController(session.jira, session.sprint_name)
    view = TimeView()
    
    summary_data = controller.get_weekly_summary(session.user_email, all_tickets)
    view.show_weekly_summary(summary_data, controller.jira_url)


def view_time_by_ticket(session, status_filter=None):
    """View time logged by ticket."""
    controller = TimeController(session.jira, session.sprint_name)
    view = TimeView()
    
    time_data = controller.get_time_by_ticket(session.user_email, status_filter)
    view.show_time_by_ticket(time_data, controller.jira_url)


def main():
    """Main entry point."""
    # Initialize session
    session = JiraSession()
    
    # Create menu
    menu = Menu("TIME LOGGING MENU")
    menu.add_item("1", "Weekly summary", "(sprint tickets only)",
                  action=lambda: view_weekly_summary(session, all_tickets=False), color=Colors.CYAN)
    menu.add_item("2", "Weekly summary", "(all tickets)",
                  action=lambda: view_weekly_summary(session, all_tickets=True), color=Colors.BLUE)
    menu.add_item("3", "View time by ticket", "(all)",
                  action=lambda: view_time_by_ticket(session, status_filter=None), color=Colors.YELLOW)
    menu.add_item("4", "View time by ticket", "(In Progress only)",
                  action=lambda: view_time_by_ticket(session, status_filter='In Progress'), color=Colors.HEADER)
    menu.add_item("5", "Log time to ticket", None,
                  action=lambda: log_time_interactive(session), color=Colors.GREEN)
    menu.add_item("0", "Exit", color=Colors.RED)
    
    # Run menu
    menu.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
