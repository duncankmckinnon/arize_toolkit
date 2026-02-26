import json
import sys
from typing import Any, Dict, List, Optional, Sequence

import click
from rich.console import Console
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def print_json(data: Any) -> None:
    click.echo(json.dumps(data, indent=2, default=str))


def print_table(
    data: List[Dict[str, Any]],
    columns: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
) -> None:
    if not data:
        console.print("[dim]No results found.[/dim]")
        return

    if columns is None:
        columns = list(data[0].keys())

    table = Table(title=title, show_lines=False)
    for col in columns:
        table.add_column(col, overflow="fold")

    for row in data:
        table.add_row(*(str(row.get(col, "")) for col in columns))

    console.print(table)


def print_result(
    data: Any,
    columns: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    json_mode: bool = False,
) -> None:
    if json_mode:
        print_json(data)
        return

    if isinstance(data, list):
        print_table(data, columns=columns, title=title)
    elif isinstance(data, dict):
        print_table([data], columns=columns, title=title)
    else:
        console.print(data)


def print_success(msg: str) -> None:
    console.print(f"[green]{msg}[/green]")


def print_error(msg: str) -> None:
    error_console.print(f"[red]Error: {msg}[/red]")
    sys.exit(1)


def print_url(url: str, label: Optional[str] = None) -> None:
    if label:
        console.print(f"[green]{label}:[/green] {url}")
    else:
        console.print(url)
