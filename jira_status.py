#!/usr/bin/env python3
"""
Ticket Status - View all tickets grouped by status.
Coordinator between StatusController and StatusView.
"""
import sys
from jira_lib import JiraSession
from controllers.status import StatusController
from ui.ui_status import StatusView


def _show_status_group(status, issues, totals, view, *, as_subgroup=False):
    """Render a single status group (tickets + time total)."""
    count = len(issues)
    if as_subgroup:
        view.show_status_subgroup(status, count)
    else:
        view.show_status_group(status, count)
    for issue in issues:
        view.show_ticket(issue)
    if totals.get(status, 0) > 0:
        view.show_status_total_time(status, totals[status])


def main():
    """Main entry point."""
    # Initialize session
    session = JiraSession()
    
    # Initialize controller and view
    controller = StatusController(session.jira, session.sprint_name, session.user_email)
    view = StatusView(session.jira_url)
    
    # Display header
    view.show_header()
    
    # Show sprint context
    if session.sprint_name:
        view.show_sprint_name(session.sprint_name)
    else:
        view.show_no_sprint_warning()
    
    # Get tickets from controller
    issues = controller.get_tickets()
    view.show_ticket_count(len(issues))
    
    # Group issues by status
    issues_by_status = controller.group_by_status(issues)
    status_totals = controller.calculate_status_totals(issues)
    
    # Get display order
    primary_statuses = controller.get_primary_statuses()
    all_statuses = controller.get_status_order()
    
    # Display primary statuses
    for status in primary_statuses:
        if status in issues_by_status:
            _show_status_group(status, issues_by_status[status], status_totals, view)

    # Display other statuses
    other_statuses = [s for s in issues_by_status.keys() if s not in primary_statuses]
    if other_statuses:
        view.show_other_statuses_header()
        for status in other_statuses:
            _show_status_group(status, issues_by_status[status], status_totals, view, as_subgroup=True)
    
    # Display footer
    view.show_footer()
    view.show_done()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
