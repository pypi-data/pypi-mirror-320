import typer

from pipeline_ui.modules.auth.auth import check_access_token, write_access_token


def login():
    """
    Login to the registry
    """
    typer.echo("Please retrieve your access token from pipelineui.com/settings")
    access_token = typer.prompt("Enter your access token", hide_input=True)

    if access_token and check_access_token(access_token):
        write_access_token(access_token)
    else:
        typer.echo("Login failed. Please provide a valid access token.")
