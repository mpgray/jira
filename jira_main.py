#!/usr/bin/env python3
"""
Main menu for Jira management tools.

Provides access to:
1. Daily ticket updates
2. Time logging
3. Ticket status view
"""

import sys
import subprocess
from ui import print_header, print_menu_item, prompt, Colors


def run_script(script_name):
    """Run a Python script in the virtual environment."""
    venv_python = '.venv/bin/python'
    try:
        subprocess.run([venv_python, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error running {script_name}")
        print(f"Details: {str(e)}")
    except KeyboardInterrupt:
        print(f"\n\n[WARN] {script_name} interrupted by user")


def main():
    """Main menu loop."""
    while True:
        print_header("JIRA MANAGEMENT MENU")
        print()
        print_menu_item(1, "Daily Ticket Updates", "Process Open and Queue tickets", Colors.BLUE)
        print_menu_item(2, "Log Time", "View and log time to tickets", Colors.GREEN)
        print_menu_item(3, "Ticket Status", "View all tickets by status", Colors.YELLOW)
        print_menu_item(0, "Exit", color=Colors.RED)
        
        choice = prompt("\nEnter choice (0-3):")
        
        if choice == '1':
            print("\n" + "-" * 80)
            print("Running Daily Ticket Updates...")
            print("-" * 80 + "\n")
            run_script('jira_updates.py')
        elif choice == '2':
            print("\n" + "-" * 80)
            print("Running Time Logging...")
            print("-" * 80 + "\n")
            run_script('jira_time.py')
        elif choice == '3':
            print("\n" + "-" * 80)
            print("Running Ticket Status View...")
            print("-" * 80 + "\n")
            run_script('jira_status.py')
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("\n[ERROR] Invalid choice. Please enter 0-3.")
        
        # Wait for user after script completes
        if choice in ['1', '2', '3']:
            input("\nPress Enter to return to main menu...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        sys.exit(1)
