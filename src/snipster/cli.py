import typer
from decouple import config
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from snipster.db import create_db_and_tables, get_engine
from snipster.models import Snippet
from snipster.repo import DatabaseSnippetRepository

app = typer.Typer(help="Snipster: manage code snippets.", no_args_is_help=True)

console = Console()
DB_URL = config("DB_URL")


@app.command()
def init():
    """
    Initialize the Snipster database (create file + tables).
    """
    console.rule("[bold green]Initializing Snipster")

    engine = get_engine(DB_URL)
    create_db_and_tables(engine)

    console.print("[bold green]Database initialized![/bold green]")
    console.print(f"Location: [cyan]{DB_URL}[/cyan]")


@app.callback()
def load_repo(ctx: typer.Context):
    """
    Load the database and repository once per CLI call.
    """
    engine = get_engine(DB_URL)
    create_db_and_tables(engine)
    ctx.obj = DatabaseSnippetRepository(engine)


@app.command()
def add(ctx: typer.Context, title: str, code: str, description: str = ""):
    repo = ctx.obj

    snippet = Snippet(title=title, code=code, description=description)
    repo.add(snippet)

    console.print(
        f"[bold green]Added snippet #{snippet.id}[/bold green]: {snippet.title}"
    )


@app.command("list")
def list_snippets(ctx: typer.Context):
    repo = ctx.obj
    snippets = repo.list()

    if not snippets:
        console.print("No snippets found.")
        raise typer.Exit()

    table = Table(title="Your Snippets")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Fav", style="yellow")
    table.add_column("Title", style="bold white")

    for snippet in snippets:
        fav = "⭐" if snippet.favourite else ""
        table.add_row(str(snippet.id), fav, snippet.title)

    console.print(table)


@app.command()
def search(ctx: typer.Context, text: str):
    repo = ctx.obj
    results = repo.search(text)

    if not results:
        console.print(f"No snippets found matching '{text}'.")
        raise typer.Exit()

    table = Table(title=f"Search results for '{text}'")

    table.add_column("ID", style="cyan")
    table.add_column("Fav", style="yellow")
    table.add_column("Title", style="bold white")

    for snippet in results:
        fav = "⭐" if snippet.favourite else ""
        table.add_row(str(snippet.id), fav, snippet.title)

    console.print(table)


@app.command()
def get(ctx: typer.Context, snippet_id: int):
    repo = ctx.obj
    snippet = repo.get(snippet_id)

    if not snippet:
        console.print(f"No snippet found with id {snippet_id}")
        raise typer.Exit()

    console.rule(f"[bold cyan]Snippet #{snippet.id}: {snippet.title}")

    syntax = Syntax(snippet.code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    if snippet.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(snippet.description)


@app.command()
def delete(ctx: typer.Context, snippet_id: int):
    repo = ctx.obj
    snippet = repo.get(snippet_id)

    if not snippet:
        console.print(f"No snippet with id {snippet_id}")
        raise typer.Exit()

    repo.delete(snippet_id)
    console.print(f"Deleted snippet #{snippet_id}.")


@app.command()
def favourite(ctx: typer.Context, snippet_id: int):
    repo = ctx.obj
    snippet = repo.get(snippet_id)

    if not snippet:
        console.print(f"No snippet with id {snippet_id}")
        raise typer.Exit()

    repo.favourite(snippet_id)
    console.print(f"⭐ Snippet #{snippet_id} marked as favourite!")
