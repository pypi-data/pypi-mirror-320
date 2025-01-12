"""Help menu for Arma 3 CLI"""
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box
from rich.text import Text

console = Console()

def load_help_data():
    """Load help data from JSON file"""
    data_dir = Path(__file__).parent.parent / "data"
    help_file = data_dir / "help.json"
    
    try:
        with open(help_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[red]Error: Help data file not found[/]")
        return None

def create_category_table(title: str, commands: list) -> Table:
    """Create a table for a category of commands"""
    table = Table(
        title=title,
        title_style="bold cyan",
        box=box.ROUNDED,
        expand=True,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Examples", style="yellow")
    
    for cmd in commands:
        examples = "\n".join(f"• {ex}" for ex in cmd["examples"])
        table.add_row(
            cmd["syntax"],
            cmd["description"],
            examples
        )
    
    return table

def show_help():
    """Display the help menu with rich formatting"""
    help_data = load_help_data()
    if not help_data:
        return

    # Title and description
    title_text = Text(help_data["title"], style="bold blue")
    desc_text = Text(help_data["description"], style="italic")
    
    console.print()
    console.print(Panel(title_text, style="blue"))
    console.print(Panel(desc_text, style="cyan"))
    console.print()

    # Print each category
    for category, data in help_data["categories"].items():
        table = create_category_table(category, data["commands"])
        console.print(table)
        console.print()

    # Footer
    console.print(Panel(
        "[cyan]For detailed help on any command, use:[/] [yellow]arma3cli COMMAND --help[/]",
        style="blue"
    ))
    console.print()
