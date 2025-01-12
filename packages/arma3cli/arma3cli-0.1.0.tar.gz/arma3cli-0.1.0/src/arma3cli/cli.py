"""
Main CLI entry point for Arma 3 Server CLI
"""
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option()
def main():
    """Arma 3 Server CLI - A tool for managing Arma 3 servers"""
    pass

@main.command()
def init():
    """Initialize a new Arma 3 server configuration"""
    console.print("[bold green]Initializing new Arma 3 server configuration...[/]")

@main.command()
@click.argument('server_path', type=click.Path(exists=True))
def start(server_path):
    """Start an Arma 3 server"""
    console.print(f"[bold green]Starting Arma 3 server at {server_path}[/]")

@main.command()
@click.argument('server_path', type=click.Path(exists=True))
def stop(server_path):
    """Stop an Arma 3 server"""
    console.print(f"[bold red]Stopping Arma 3 server at {server_path}[/]")

if __name__ == '__main__':
    main() 