import os

import typer
from rich.console import Console

from quantstream.config import create_project_database, set_api_key

app = typer.Typer(
    name="quantstream",
    help="`quantstream` is a Python package for financial data analysis.",
    add_completion=False,
)
console = Console()


@app.command(name="create-db")
def create_db(location: str, db_name: str):
    """Create a new SQLite database for a project."""
    create_project_database(location, db_name)
    console.print(f"Database created at {os.path.join(location, db_name)}.")

@app.command(name="set-api-key")
def set_key(api_key: str, service: str):
    """Set the API key for a specific service."""
    set_api_key(api_key, service)
    console.print(f"API key set for {service}.")


if __name__ == "__main__":
    app()
