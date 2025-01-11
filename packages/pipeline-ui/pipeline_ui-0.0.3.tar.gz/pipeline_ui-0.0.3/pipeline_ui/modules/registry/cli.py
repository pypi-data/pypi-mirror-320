import importlib.util
import os
import sys
from typing import Optional

import requests
import toml
import typer

from pipeline_ui.modules.common.dependencies import INTERNAL_SERVER_URL
from pipeline_ui.modules.pui.pui import PipelineUI
from pipeline_ui.modules.registry.registry import RegistryManager


def load_module_without_server(file_path: str, start_server: bool = True):
    # Temporarily modify PipelineUI to prevent server start
    original_start = PipelineUI.start
    if not start_server:
        PipelineUI.start = lambda self: None

    spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["dynamic_module"] = module
    spec.loader.exec_module(module)

    # Restore original start method
    PipelineUI.start = original_start

    return module

def publish(filename: str):
    """
    Publish the nodes and workflows on the registry
    """
    if not os.path.exists(filename):
        typer.echo(f"Error: File '{filename}' not found.")
        return

    # Load the module
    module = load_module_without_server(filename, start_server=False)

    # Get the PipelineUI instance
    pui : PipelineUI = module.pui

    # Get all nodes
    nodes = pui.nodes
    workflows = pui.workflows
    pack = pui.pack

    registry = RegistryManager()

    registry.publish(nodes, workflows, pack, filename)

def install(
        org_node_identifier: Optional[list[str]] = typer.Option(None, "--nodes", "-n", help="Names of nodes to install"),
        org_workflow_identifier: Optional[list[str]] = typer.Option(None, "--workflows", "-w", help="Names of workflows to install"),
    ):
    """
    Install nodes, workflows or projects from a URL
    """

    ORG = "test" # TODO: Make this dynamic

    if not org_node_identifier and not org_workflow_identifier:
        typer.echo("Error: No nodes or workflows specified")
        return
    
    if org_node_identifier and org_workflow_identifier:
        typer.echo("Error: Cannot specify both nodes and workflows")
        return

    if org_node_identifier:
        typer.echo(f"Installing nodes: {', '.join(org_node_identifier)}")

        node_folder = "nodes"  # Default value
        if os.path.exists("pyproject.toml"):

            with open("pyproject.toml", "r") as f:
                try:
                    toml_dict = toml.load(f)
                    node_folder = toml_dict.get("tool", {}).get("pui", {}).get("node_folder", node_folder)
                except:
                    pass

        # Create node folder if it doesn't exist
        os.makedirs(node_folder, exist_ok=True)

        # Install each requested node
        for node_name in org_node_identifier:
            typer.echo(f"Installing node: {node_name}")
            
            # Get source code from registry
            response = requests.get(f"{INTERNAL_SERVER_URL}/registry/source_code/{ORG}/{node_name}", 
                                headers={'accept': 'application/json'})
            response.raise_for_status()

            # Write node file
            node_path = os.path.join(node_folder, f"{node_name}.py")
            with open(node_path, "w") as f:
                f.write(response.json())

    if org_workflow_identifier:
        typer.echo(f"Installing workflow: {', '.join(org_workflow_identifier)}")

        workflow_folder = "workflows"  # Default value
        if os.path.exists("pyproject.toml"):

            with open("pyproject.toml", "r") as f:
                try:
                    toml_dict = toml.load(f)
                    workflow_folder = toml_dict.get("tool", {}).get("pui", {}).get("workflow_folder", workflow_folder)
                except:
                    pass

        # Create workflow folder if it doesn't exist
        os.makedirs(workflow_folder, exist_ok=True)

        for workflow_name in org_workflow_identifier:
            typer.echo(f"Installing workflow: {workflow_name}")

            # Get source code from registry
            response = requests.get(f"{INTERNAL_SERVER_URL}/registry/source_code/{ORG}/{workflow_name}", 
                                headers={'accept': 'application/json'})
            response.raise_for_status()

        

def publish_workflow(file: str):
    pass
