"""
Workflow View - Handles all display logic for ticket workflow operations.
"""
from ui.ui_utils import Colors, colorize, print_separator


class WorkflowView:
    """View layer for ticket workflow operations."""
    
    def show_header(self, title):
        """Display section header."""
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80 + "\n")
    
    def show_no_tickets(self, status):
        """Show no tickets found for status."""
        print(f"No tickets in '{status}' status.")
    
    def show_ticket_count(self, count, status):
        """Show count of tickets in status."""
        print(f"Found {count} ticket(s) in '{status}':\n")
    
    def show_processing_header(self, title):
        """Show processing header."""
        print(f"\n{title}")
    
    def show_ticket_with_pr(self, issue_key, summary, pr_url):
        """Show ticket with PR link."""
        print(f"\n{issue_key}: {summary}")
        print(f"  [OK] PR link detected: {pr_url}")

    def show_pr_status(self, is_merged):
        """Show PR merge status."""
        if is_merged:
            print("  [OK] PR is merged")
        else:
            print("  [OK] PR is open")
        action_map = {
            'close': 'Closed',
            'pending_review': 'Pending Review',
            'in_queue': 'In Queue',
            'in_progress': 'In Progress'
        }
        target = action_map.get(action, action)
        
        print(f"  [PREVIEW] Would transition to '{target}'")
        if comment:
            comment_preview = comment if len(comment) <= 50 else comment[:50] + "..."
            print(f"  [PREVIEW] Would add comment: {comment_preview}")
    
    def show_transition_success(self, target_status):
        """Show successful transition."""
        print(f"  [OK] Transitioned to '{target_status}' with comment")

    def show_transition_failed(self, error=None):
        """Show failed transition."""
        if error:
            print(f"  [FAIL] Failed to transition: {error}")
        else:
            print("  [FAIL] Failed to transition")
        """Show no tickets with PRs found."""
        print("No tickets with PRs found.")
    
    def show_ticket_transition(self, issue_key, summary):
        """Show ticket being transitioned."""
        print(f"\n{issue_key}: {summary}")
    
    def show_error(self, error):
        """Show error message."""
        print(f"  [ERROR] {error}")
    
    def show_open_ticket_list(self, issues):
        """Display list of open tickets for selection."""
        print("\nOPEN TICKETS:")
        for idx, issue in enumerate(issues, 1):
            priority = "None"
            if hasattr(issue.fields, 'priority') and issue.fields.priority:
                priority = issue.fields.priority.name
            print(f"  {idx}. {issue.key}: {issue.fields.summary}")
            print(f"     Priority: {priority}")
    
    def show_selection_prompt(self):
        """Show prompt for ticket selection."""
        print("\nEnter ticket numbers to queue (comma-separated, e.g., '1,3,5')")
        print("Or press Enter to skip")
    
    def show_invalid_selection(self, idx):
        """Show invalid selection warning."""
        print(f"[WARN] Invalid selection: {idx}")

    def show_invalid_input(self):
        """Show invalid input error."""
        print("[ERROR] Invalid input format")
        """Show completion message."""
        print("\nDone!")
    
    def show_mode_indicator(self, dry_run):
        """Show current mode."""
        if dry_run:
            print(f"{Colors.YELLOW}[PREVIEW MODE - No changes will be made]{Colors.ENDC}\n")
        else:
            print(f"{Colors.GREEN}[LIVE MODE - Changes will be made]{Colors.ENDC}\n")
    
    def show_processing_results(self, results, dry_run):
        """
        Show results of processing tickets.
        results: list of dicts with ticket info and action results
        """
        for result in results:
            self.show_ticket_transition(result['issue_key'], result['summary'])
            
            if 'pr_url' in result:
                print(f"  [OK] PR link: {result['pr_url']}")
                if result.get('is_merged'):
                    print("  [OK] PR is merged")
                else:
                    print("  [OK] PR is open")
            
            action = result.get('action')
            if action:
                if dry_run:
                    self.show_preview_action(action)
                else:
                    if result['success']:
                        action_map = {
                            'close': 'Closed',
                            'pending_review': 'Pending Review',
                            'in_queue': 'In Queue',
                            'in_progress': 'In Progress'
                        }
                        self.show_transition_success(action_map.get(action, action))
                    else:
                        self.show_transition_failed(result.get('error'))
