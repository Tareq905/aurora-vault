from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()

def print_signature():
    console.print("[dim]◌ Aurora-Vault v1.0 | Supervised by Tareq[/dim]")

def welcome_ui(message):
    console.print(Panel(
        f"[bold cyan]Aurora-Vault[/bold cyan]\n[white]{message}[/white]",
        expand=False
    ))

def get_progress_bar():
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console
    )