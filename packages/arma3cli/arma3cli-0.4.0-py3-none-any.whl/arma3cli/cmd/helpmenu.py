"""Help menu for Arma 3 CLI"""
import click
from rich.console import Console
from rich.table import Table

console = Console()

def show_help():
    """Display the help menu with rich formatting"""
    table = Table(title="Arma 3 Server CLI Commands")
    
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    
    table.add_row("init", "Initialize a new Arma 3 server configuration")
    table.add_row("start <path>", "Start an Arma 3 server at the specified path")
    table.add_row("stop <path>", "Stop an Arma 3 server at the specified path")
    
    console.print("\n[bold blue]Arma 3 Server CLI[/bold blue]")
    console.print("[italic]A tool for managing Arma 3 servers[/italic]\n")
    console.print(table)
    console.print("\nFor more details on each command, use: [cyan]arma3cli COMMAND --help[/cyan]")
