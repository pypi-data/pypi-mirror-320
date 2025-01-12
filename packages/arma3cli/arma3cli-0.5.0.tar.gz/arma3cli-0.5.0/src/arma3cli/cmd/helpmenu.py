"""Help menu for Arma 3 CLI"""
import json
import os
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Static

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

class CommandCategory(Static):
    """A category of commands with its own styling"""
    
    def __init__(self, title: str, commands: list):
        super().__init__()
        self.title = title
        self.commands = commands
    
    def compose(self) -> ComposeResult:
        table = Table(
            title=self.title,
            title_style="bold cyan",
            box=None,
            padding=(0, 1),
            expand=True
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Examples", style="yellow")
        
        for cmd in self.commands:
            examples = "\n".join(cmd["examples"])
            table.add_row(
                cmd["syntax"],
                cmd["description"],
                examples
            )
        
        yield Static(table)

class HelpApp(App):
    """The main help application"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #help-container {
        width: 90%;
        height: 90%;
        border: solid green;
        background: $surface;
    }
    
    .title {
        text-align: center;
        padding: 1;
    }
    
    Footer {
        background: $primary-background;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        help_data = load_help_data()
        
        yield Header(show_clock=True)
        
        with ScrollableContainer(id="help-container"):
            yield Static(
                Text(help_data["title"], style="bold blue"),
                classes="title"
            )
            yield Static(
                Text(help_data["description"], style="italic"),
                classes="title"
            )
            
            with Vertical():
                for category, data in help_data["categories"].items():
                    yield CommandCategory(category, data["commands"])
        
        yield Footer()

def show_help():
    """Display the help menu with Textual UI"""
    app = HelpApp()
    app.run()
