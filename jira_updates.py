#!/usr/bin/env python3
"""
Daily Updates - Daily ticket workflow management.
Coordinator between WorkflowController and WorkflowView.
"""
import sys
from jira_lib import JiraSession
from ui import Menu, Colors
from controllers.workflow import WorkflowController
from ui.ui_workflow import WorkflowView

# Comment templates
QUEUE_COMMENT = "When these tickets are set up and ready for parent story to be QA'd, this ticket will be next in progress."
IN_PROGRESS_COMMENT = "This story has started work."
PENDING_REVIEW_COMMENT = "Pull Request is open and ready for review."
CLOSED_COMMENT = "Pull Request has been merged. Work is complete."


def check_prs_interactive(controller, view, dry_run):
    """Check in progress tickets for PRs and handle transitions."""
    view.show_header("CHECKING IN PROGRESS TICKETS FOR PRs")
    view.show_mode_indicator(dry_run)
    
    # Process tickets with PRs
    results = controller.process_tickets_with_prs(
        dry_run=dry_run,
        pending_comment=PENDING_REVIEW_COMMENT,
        closed_comment=CLOSED_COMMENT
    )
    
    if results:
        view.show_processing_results(results, dry_run)
    else:
        view.show_no_pr_tickets()
    
    view.show_done()


def select_open_to_queue_interactive(controller, view):
    """Interactively select open tickets to move to queue."""
    view.show_header("SELECT OPEN TICKETS TO MOVE TO IN QUEUE")
    
    # Get open tickets
    open_tickets = controller.get_open_tickets()
    
    if not open_tickets:
        print("No Open tickets found in sprint.")
        return
    
    # Display tickets
    view.show_open_ticket_list(open_tickets)
    view.show_selection_prompt()
    
    # Get selection
    selection = input("\nYour selection: ").strip()
    
    if not selection:
        print("Skipped.")
        return
    
    # Parse selection
    try:
        indices = [int(x.strip()) for x in selection.split(',')]
        selected_keys = []
        
        for idx in indices:
            if 1 <= idx <= len(open_tickets):
                selected_keys.append(open_tickets[idx-1].key)
            else:
                view.show_invalid_selection(idx)
        
        if selected_keys:
            # Move tickets (always live mode for this interactive operation)
            results = controller.move_tickets_to_queue(selected_keys, QUEUE_COMMENT, dry_run=False)
            view.show_processing_results(results, False)
        
    except ValueError:
        view.show_invalid_input()


def move_queue_to_progress_interactive(controller, view, dry_run):
    """Move all in queue tickets to in progress."""
    view.show_header("MOVING IN QUEUE TICKETS TO IN PROGRESS")
    view.show_mode_indicator(dry_run)
    
    queue_tickets = controller.get_queue_tickets()
    
    if not queue_tickets:
        view.show_no_tickets('In Queue')
        return
    
    view.show_ticket_count(len(queue_tickets), 'In Queue')
    
    # Show tickets
    for issue in queue_tickets:
        print(f"{issue.key}: {issue.fields.summary}")
    
    print()
    
    # Move tickets
    results = controller.move_queue_to_progress(IN_PROGRESS_COMMENT, dry_run=dry_run)
    view.show_processing_results(results, dry_run)
    
    view.show_done()


def main():
    """Main entry point."""
    # Initialize session
    session = JiraSession()
    
    # Initialize controller and view
    controller = WorkflowController(session.jira, session.sprint_name)
    view = WorkflowView()
    
    # Track mode
    dry_run = [True]  # Use list to allow mutation in lambda
    
    def toggle_mode():
        """Toggle between preview and live mode."""
        dry_run[0] = not dry_run[0]
        mode = "PREVIEW" if dry_run[0] else "LIVE"
        print(f"\n{Colors.YELLOW}→{Colors.ENDC} Switched to {Colors.BOLD}{mode}{Colors.ENDC} mode\n")
    
    # Create menu with dynamic mode display
    while True:
        mode_text = "PREVIEW MODE" if dry_run[0] else "LIVE MODE"
        mode_color = Colors.YELLOW if dry_run[0] else Colors.GREEN
        
        menu = Menu(f"DAILY TICKET UPDATES - {mode_color}{mode_text}{Colors.ENDC}")
        
        menu.add_item("1", "Check In Progress for PRs", "(auto transitions)",
                      action=lambda: check_prs_interactive(controller, view, dry_run[0]),
                      color=Colors.CYAN)
        menu.add_item("2", "Select Open tickets", "(move to Queue)",
                      action=lambda: select_open_to_queue_interactive(controller, view),
                      color=Colors.BLUE)
        menu.add_item("3", "Move Queue→In Progress", "(all queued)",
                      action=lambda: move_queue_to_progress_interactive(controller, view, dry_run[0]),
                      color=Colors.GREEN)
        
        toggle_text = "Switch to LIVE mode" if dry_run[0] else "Switch to PREVIEW mode"
        menu.add_item("m", toggle_text, None,
                      action=toggle_mode, color=Colors.YELLOW)
        
        menu.add_item("0", "Exit", color=Colors.RED)
        
        # Display and handle choice
        menu.display()
        choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()
        
        if choice == '0':
            print(f"\n{Colors.GREEN}[OK]{Colors.ENDC} Exiting...\n")
            break
        
        if not menu.handle_choice(choice):
            print(f"\n{Colors.RED}[ERROR]{Colors.ENDC} Invalid option. Please try again.\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
