"""
Unified menu system for consistent menu handling across all scripts.
"""
from .ui_utils import print_header, print_menu_item, prompt, print_error, colorize, Colors


class MenuItem:
    """Represents a single menu item."""
    
    def __init__(self, key, title, description=None, action=None, color=None):
        """
        Create a menu item.
        
        Args:
            key: Menu item key (number or string)
            title: Item title
            description: Optional description
            action: Callable to execute when selected
            color: Optional color for the title
        """
        self.key = str(key)
        self.title = title
        self.description = description
        self.action = action
        self.color = color or Colors.BLUE


class Menu:
    """
    Generic menu system with consistent display and input handling.
    
    Example:
        menu = Menu("My Menu", mode="LIVE MODE")
        menu.add_item("1", "Option 1", action=func1)
        menu.add_item("0", "Exit", color=Colors.RED)
        menu.run()
    """
    
    def __init__(self, title, mode=None, sprint_name=None):
        """
        Create a menu.
        
        Args:
            title: Menu title
            mode: Optional mode indicator (e.g., "PREVIEW MODE")
            sprint_name: Optional sprint name to display
        """
        self.title = title
        self.mode = mode
        self.sprint_name = sprint_name
        self.items = []
        self.running = True
    
    def add_item(self, key, title, description=None, action=None, color=None):
        """
        Add a menu item.
        
        Args:
            key: Menu item key (number or string)
            title: Item title
            description: Optional description
            action: Callable to execute when selected
            color: Optional color for the title
        """
        item = MenuItem(key, title, description, action, color)
        self.items.append(item)
    
    def display(self):
        """Display the menu."""
        print_header(self.title, self.mode)
        if self.sprint_name:
            print(f"Sprint: {colorize(self.sprint_name, Colors.BOLD)}\n")
        
        for item in self.items:
            print_menu_item(item.key, item.title, item.description, item.color)
    
    def get_valid_keys(self):
        """Get list of valid menu keys."""
        return [item.key for item in self.items]
    
    def find_item(self, key):
        """Find menu item by key."""
        for item in self.items:
            if item.key == key:
                return item
        return None
    
    def handle_choice(self, choice):
        """
        Handle a menu choice.
        
        Args:
            choice: User's choice
            
        Returns:
            True to continue menu loop, False to exit
        """
        item = self.find_item(choice)
        
        if not item:
            valid_keys = ", ".join(self.get_valid_keys())
            print_error(f"Invalid choice. Please enter one of: {valid_keys}")
            return True
        
        # Check if this is an exit item (key "0" or title contains "Exit")
        if item.key == "0" or "exit" in item.title.lower():
            print("\nGoodbye!")
            return False
        
        # Execute the action if provided
        if item.action:
            try:
                item.action()
            except KeyboardInterrupt:
                print("\n\n[WARN] Operation interrupted by user")
            except Exception as e:
                print_error(f"Error: {str(e)}")
        
        return True
    
    def run(self):
        """
        Run the menu loop.
        
        Returns when user selects exit option.
        """
        while self.running:
            self.display()
            
            valid_keys = self.get_valid_keys()
            if len(valid_keys) > 2:  # More than just 0 and 1 option
                min_key = min(int(k) for k in valid_keys if k.isdigit())
                max_key = max(int(k) for k in valid_keys if k.isdigit())
                prompt_text = f"\nEnter choice ({min_key}-{max_key}):"
            else:
                prompt_text = f"\nEnter choice ({', '.join(valid_keys)}):"
            
            choice = prompt(prompt_text)
            
            if not self.handle_choice(choice):
                break
    
    def stop(self):
        """Stop the menu loop."""
        self.running = False
