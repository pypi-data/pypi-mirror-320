import asyncio
from typing import Dict, Tuple, Any

import aiohttp
from pipeline_ui.modules.pack.pack import Pack
import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TaskID
from rich.status import Status

from pipeline_ui.modules.auth.auth import load_access_token
from pipeline_ui.modules.common.dependencies import INTERNAL_SERVER_URL
from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.workflow.workflow import Workflow
import requests

class RegistryManager:
    def __init__(self):
        self.console = Console()
        self.base_url = INTERNAL_SERVER_URL
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": load_access_token()
        }


#         function_info_dict = extract_function_code_recursive(main_function)
# for func_name, info in function_info_dict.items():
#     print(f"\n=== {func_name} ===")
#     print(f"Source:\n{info.source_code}")
#     print(f"Is async: {info.is_async}")
#     print(f"Decorators: {info.decorators}")
#     print(f"Calls: {info.called_functions}")
#     print(f"Docstring: {info.docstring}")

# # You can also get JSON representation
# json_data = function_info_dict['main_function'].model_dump_json(indent=2)

    def publish_pack(self, pack: Pack) -> dict:
        """Publish a single pack using aiohttp."""
        url = f"{self.base_url}/packs/"
        
        response = requests.post(url, headers=self.headers, json=pack.to_json())
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to publish pack {pack.name} with status {response.status_code} and message: {response.text}, cannot proceed without a pack")

    async def publish_node(self, session: aiohttp.ClientSession, name: str, node: Node, progress: Progress, task_id: TaskID, published_pack_id: str) -> Tuple[dict, str]:
        """Publish a single node using aiohttp."""
        url = f"{self.base_url}/nodes/"
        try:
            async with session.post(url, headers=self.headers, json=node.to_json(published_pack_id)) as response:
                try:
                    result = await response.json()
                except aiohttp.ContentTypeError:
                    result = await response.text()
                if response.status == 200:
                    progress.update(task_id, description=f"Published node [{name}] ✅")
                    progress.remove_task(task_id)
                    return result, name
                else:
                    progress.update(task_id, description=f"Failed to publish node [{name}] ❌")
                    progress.remove_task(task_id)
                    self.console.print(f"❌ Publishing node {name} failed with status {response.status} and message: {result}")
                    return {"error": result}, name
        except Exception as e:
            progress.update(task_id, description=f"Failed to publish node [{name}] ❌")
            progress.remove_task(task_id)
            self.console.print(f"❌ Publishing node {name} failed: {str(e)}")
            return {"error": str(e)}, name

    async def publish_workflow(self, session: aiohttp.ClientSession, name: str, workflow: Workflow, progress: Progress, task_id: TaskID, published_pack_id: str) -> Tuple[dict, str]:
        """Publish a single workflow using aiohttp."""
        url = f"{self.base_url}/workflows/"
        # print("published_pack_id", published_pack_id)
        # raise NotImplementedError("TODO workflow publish")
        try:
            async with session.post(url, headers=self.headers, json=workflow.to_json(published_pack_id)) as response:
                try:
                    result = await response.json()
                except aiohttp.ContentTypeError:
                    result = await response.text()
                if response.status == 200:
                    progress.update(task_id, description=f"Published workflow [{name}] ✅")
                    progress.remove_task(task_id)
                    return result, name
                else:
                    progress.update(task_id, description=f"Failed to publish workflow [{name}] ❌")
                    progress.remove_task(task_id)
                    self.console.print(f"❌ Publishing workflow {name} failed with status {response.status} and message: {result}")
                    return {"error": result}, name
        except Exception as e:
            progress.update(task_id, description=f"Failed to publish workflow [{name}] ❌")
            progress.remove_task(task_id)
            self.console.print(f"❌ Publishing workflow {name} failed: {str(e)}")
            return {"error": str(e)}, name

    async def publish_all(self, nodes: Dict[str, Node], workflows: Dict[str, Workflow], published_pack_id: str):
        """Publish all nodes and workflows concurrently with progress tracking."""
        async with aiohttp.ClientSession() as session:
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                console=self.console,
                transient=False,
                expand=True
            ) as progress:
                # Create tasks for nodes and workflows
                node_tasks = []
                workflow_tasks = []
                
                # Add progress tasks and create publish tasks
                for name, node in nodes.items():
                    task_id = progress.add_task(f"Publishing node [{name}]...", total=None)
                    node_tasks.append(self.publish_node(session, name, node, progress, task_id, published_pack_id))
                
                for name, workflow in workflows.items():
                    task_id = progress.add_task(f"Publishing workflow [{name}]...", total=None)
                    workflow_tasks.append(self.publish_workflow(session, name, workflow, progress, task_id, published_pack_id))
                
                # Run all tasks concurrently
                all_results = await asyncio.gather(*(node_tasks + workflow_tasks), return_exceptions=True)
                return all_results

    def publish(self, nodes: Dict[str, Node], workflows: Dict[str, Workflow], pack: Pack, filename: str):
        """Main publish method with progress tracking."""
        if not nodes and not workflows:
            typer.echo("No nodes or workflows found in the specified file.")
            return

        if nodes:
            typer.echo(f"Found {len(nodes)} node(s) in {filename}:")
            for name in nodes.keys():
                typer.echo(f"  - {name}")

        if workflows:
            typer.echo(f"Found {len(workflows)} workflow(s) in {filename}:")
            for name in workflows.keys():
                typer.echo(f"  - {name}")

        published_pack = self.publish_pack(pack)
        assert published_pack["id"] is not None, "Pack id is required to publish nodes and workflows"
        published_pack_id = published_pack["id"]

        typer.echo("Starting publication process...\n")
        
        # Run the async publishing
        asyncio.run(self.publish_all(nodes, workflows, published_pack_id))

    def download(self, id: str, remove_pui: bool = False):
        # need to compute on the server how to remove the pui data, ideally should be on the client... and maybe validation on the server too
        if remove_pui:
            raise NotImplementedError("TODO Removing pui info and get a normal python function is not implemented yet")
        pass