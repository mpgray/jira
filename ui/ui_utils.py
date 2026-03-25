"""
UI utilities for consistent formatting and colors across all menus.
"""

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


def colorize(text, color):
    """Apply color to text."""
    return f"{color}{text}{Colors.ENDC}"


def print_header(title, mode=None):
    """
    Print a colored header for menus.
    
    Args:
        title: Header title text
        mode: Optional mode text (e.g., 'PREVIEW MODE', 'LIVE MODE')
    """
    print("\n" + colorize("=" * 80, Colors.CYAN))
    print(colorize(title, Colors.CYAN + Colors.BOLD))
    if mode:
        if 'PREVIEW' in mode:
            print(colorize(f"[PREVIEW] {mode}", Colors.YELLOW + Colors.BOLD))
        elif 'LIVE' in mode:
            print(colorize(f"[LIVE] {mode}", Colors.RED + Colors.BOLD))
        else:
            print(colorize(mode, Colors.BOLD))
    print(colorize("=" * 80, Colors.CYAN))


def print_menu_item(number, title, description=None, color=None):
    """
    Print a colored menu item.
    
    Args:
        number: Menu item number
        title: Item title
        description: Optional description
        color: Color for the title (defaults to BLUE)
    """
    if color is None:
        color = Colors.BLUE
    
    num_str = colorize(f'{number}.', Colors.BOLD)
    title_str = colorize(title, color)
    
    if description:
        print(f"{num_str} {title_str} - {description}")
    else:
        print(f"{num_str} {title_str}")


def prompt(text, color=Colors.BOLD):
    """
    Display a colored prompt and get input.
    
    Args:
        text: Prompt text
        color: Color for the prompt
        
    Returns:
        User input string
    """
    return input(f"{colorize(text, color)} ").strip()


def print_section(title, color=Colors.BOLD):
    """Print a section header."""
    print(f"\n{colorize(title, color)}")


def print_success(message):
    """Print a success message."""
    print(colorize(f"[OK] {message}", Colors.GREEN))


def print_error(message):
    """Print an error message."""
    print(colorize(f"[ERROR] {message}", Colors.RED))


def print_warning(message):
    """Print a warning message."""
    print(colorize(f"[WARN] {message}", Colors.YELLOW))


def print_info(message):
    """Print an info message."""
    print(colorize(f"[INFO] {message}", Colors.CYAN))


def make_ticket_link(ticket_key, jira_url):
    """
    Create a clickable link for a Jira ticket using OSC 8 escape sequence.
    
    Args:
        ticket_key: Jira ticket key (e.g., 'PROJECT-1234')
        jira_url: Base Jira URL (e.g., 'https://your-domain.atlassian.net')
        
    Returns:
        String with clickable link escape codes
    """
    return f"\033]8;;{jira_url}/browse/{ticket_key}\033\\{ticket_key}\033]8;;\033\\"


# --- Separators and Dividers ---

def print_separator(width=80, char='=', color=None):
    """
    Print a separator line.
    
    Args:
        width: Width of the separator
        char: Character to use for separator
        color: Optional color
    """
    line = char * width
    if color:
        print(colorize(line, color))
    else:
        print(line)


def print_divider(width=80, color=None):
    """Print a divider line (dash)."""
    print_separator(width, '-', color)


# --- Status Indicators ---

def print_success_icon(message):
    """Print message with success indicator."""
    print(colorize(f"  [OK] {message}", Colors.GREEN))


def print_error_icon(message):
    """Print message with error indicator."""
    print(colorize(f"  [ERROR] {message}", Colors.RED))


def print_warning_icon(message):
    """Print message with warning indicator."""
    print(colorize(f"  [WARN] {message}", Colors.YELLOW))


def print_preview_icon(message):
    """Print message with preview indicator."""
    print(colorize(f"  [PREVIEW] {message}", Colors.CYAN))


def print_ticket_icon(ticket_key, summary, extra=""):
    """Print ticket with label."""
    print(f"  {colorize(ticket_key, Colors.BOLD)} - {summary}{extra}")


def print_target_icon(message):
    """Print message with arrow indicator."""
    print(f"  --> {message}")


# --- Section Headers ---

def print_section_header(title, width=80, char='=', color=Colors.BOLD):
    """
    Print a section header with separators.
    
    Args:
        title: Section title
        width: Width of separators
        char: Character for separators
        color: Color for title
    """
    print(f"\n{char * width}")
    print(colorize(title, color))
    print(char * width)


def print_subsection(title, width=80, color=None):
    """
    Print a subsection header with dash separator.
    
    Args:
        title: Subsection title
        width: Width of separator
        color: Optional color for title
    """
    print(f"\n{title}")
    print_divider(width, color)


# --- Summary and Info Boxes ---

def print_summary_box(title, items, width=60):
    """
    Print a summary box with title and items.
    
    Args:
        title: Box title
        items: Dictionary of label: value pairs or list of strings
        width: Width of the box
    """
    print(f"\n{'=' * width}")
    print(title)
    if isinstance(items, dict):
        for label, value in items.items():
            print(f"  - {label}: {value}")
    else:
        for item in items:
            print(f"  - {item}")
    print('=' * width)


# --- Time Formatting ---

def format_time_display(seconds):
    """
    Format seconds into a human-readable time string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m", "45m", "1h 15m")
    """
    if seconds is None or seconds == 0:
        return ""
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    return f"{minutes}m"


def format_time_with_hours(seconds):
    """
    Format seconds into time string with decimal hours.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m (2.50 hours)")
    """
    time_str = format_time_display(seconds)
    hours = seconds / 3600
    return f"{time_str} ({hours:.2f} hours)"
