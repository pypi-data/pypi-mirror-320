import rich
import rich_click as click
from rich.table import Table

from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession
from codegen.cli.utils.codemod_manager import CodemodManager
from codegen.cli.workspace.decorators import requires_init


@click.command(name="list")
@requires_auth
@requires_init
def list_command(session: CodegenSession):
    """List all available codemods."""
    codemods = CodemodManager.list()

    if not codemods:
        rich.print("[yellow]No codemods found.[/yellow]")
        rich.print("\nCreate one with:")
        rich.print("  [blue]codegen create <name>[/blue]")
        return

    table = Table(title="Available Codemods", border_style="blue")
    table.add_column("Name", style="cyan")

    for codemod in codemods:
        name = codemod.name
        table.add_row(name)

    rich.print(table)
    rich.print("\nRun a codemod with:")
    rich.print("  [blue]codegen run <name>[/blue]")
