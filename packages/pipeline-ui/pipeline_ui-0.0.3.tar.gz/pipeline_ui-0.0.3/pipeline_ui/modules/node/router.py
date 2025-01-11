from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from pipeline_ui.modules.node.schema.node_schema import NodeSchema
from pipeline_ui.modules.pui.pui import PipelineUI

router = APIRouter()

class FunctionArgs(BaseModel):
    args: Dict[str, Any]


@router.get("/api/nodes", response_model=List[NodeSchema])
async def get_nodes(request: Request, filter_nodes: Optional[List[str]] = Query(None)):
    nodes = []

    pui: PipelineUI = request.app.state.pui
    for node in pui.nodes.values():
        nodes.append(node.to_schema())

    return nodes

@router.post("/api/run/{node_name}")
async def run_node(request: Request, node_name: str, node_args: FunctionArgs):
    """
    Run a specific node with the given arguments.

    Args:
        node_name (str): The name of the node to run.
        node_args (FunctionArgs): The arguments to pass to the node.

    Returns:
        dict: The result of the node execution.

    Raises:
        HTTPException: If the node is not found or if there's an error during execution.

    Example:
        To run the 'add_numbers' node:

        ```
        POST /api/run/add_numbers
        {
            "args": {
                "a": 5,
                "b": 3
            }
        }
        ```

        Response:
        ```
        {
            "out1": 8
        }
        ```
    """

    pui: PipelineUI = request.app.state.pui
    if node_name not in pui.nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node = pui.nodes[node_name]
    func = node.func
    outputs = node.outputs

    try:
        # Validate input
        result = func(**node_args.args)

        # Format the result
        # if isinstance(result, tuple):
        #     return {name: value for name, value in zip(outputs, result)}
        # else:
        return dict(zip(outputs, result))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
