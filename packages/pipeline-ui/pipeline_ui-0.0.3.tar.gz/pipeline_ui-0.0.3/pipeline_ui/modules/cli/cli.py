import importlib.util
import os
from pathlib import Path
import subprocess
import sys

import typer

from pipeline_ui.modules.auth.auth import check_access_token, write_access_token
from pipeline_ui.modules.pui.pui import PipelineUI
from pipeline_ui.modules.registry.cli import publish, install
from pipeline_ui.modules.auth.cli import login
from pipeline_ui.modules.pack.cli import init

app = typer.Typer()

app.command()(login)
app.command()(publish)
app.command()(install)
app.command()(init)

def generate_types(file: str):
    """
    Generate the types for the nodes, so that you get a list of nodes and you are sure that the nodes are correct when doing positioning
    """
    pass


@app.command()
def start(
    file_path: str = typer.Argument(
        ...,
        help="Path to the Python file to run (e.g., pipeline_ui/examples/simple.py)"
    ),
    disable_ui: bool = typer.Option(
        False,
        help="Disable the UI (only keep the backend)"
    ),
):
    """
    Run development server with hot reloading for pipeline_ui.
    Uses current Python interpreter and sets DEBUG environment variable.
    """

    # Validate file path
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        typer.echo(f"File not found: {file_path}")
        raise typer.Exit(1)
    
    # Get the current Python interpreter
    python_executable = sys.executable
    
    # Construct the command
    env = dict(os.environ)
    if disable_ui:
        env["DISABLE_UI"] = "True"
    
    # Execute the command
    try:
        watch_dir = "pipeline_ui"
        if os.path.exists(watch_dir):
            # watch the pipeline_ui directory for development (project contributor)
            cmd = f"watchfiles '{python_executable} {file_path}' {watch_dir}"
        else:
            # watch the current directory for user of the package
            cmd = f"watchfiles '{python_executable} {file_path}'"
        process = subprocess.Popen(
            cmd,
            shell=True,
            env=env
        )
        process.wait()
    except KeyboardInterrupt:
        typer.echo("\nStopping development server...")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
