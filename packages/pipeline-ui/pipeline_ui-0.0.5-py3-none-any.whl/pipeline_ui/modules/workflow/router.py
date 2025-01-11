import json
from threading import Thread
from typing import Any, Dict, Generator, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from pipeline_ui.modules.pui.pui import PipelineUI
from pipeline_ui.modules.workflow.schema.internal.schema import (
    EdgeSource,
    EdgeTarget,
    NodeParameter,
    WorkflowEdge,
    WorkflowSchema,
)

router = APIRouter()

# , response_model_exclude_none=True
@router.get("/api/workflows", response_model=List[WorkflowSchema], response_model_exclude_none=True)
async def get_workflows(request: Request) -> List[WorkflowSchema]:
    pui: PipelineUI = request.app.state.pui
    workflows = []

    for workflow in pui.workflows.values():
        # Convert to Pydantic model
        workflows.append(workflow.to_schema())

    return workflows

@router.get("/api/workflows/artifacts/{artifact_id}")
async def get_artifact(request: Request, artifact_id: str):
    pui: PipelineUI = request.app.state.pui
    # return pui.render_manager.artifacts[artifact_id]
    if artifact_id not in pui.render_manager.artifacts:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")
    return FileResponse(pui.render_manager.artifacts[artifact_id])




def generate_stream(func, pui: PipelineUI) -> Generator[str, None, None]:
    def run_task():
        func()
        pui.stream_state_manager.output_queue.put(None)  # Signal end of stream
    
    thread = Thread(target=run_task)
    thread.start()

    yield "[\n"
    first_message = True
    
    while True:
        message = pui.stream_state_manager.output_queue.get()
        if message is None:
            break
        print("message", message)
        if 'func_output' in message:
            del message['func_output']
        if first_message:
            yield json.dumps(message) + "\n"
            first_message = False
        else:
            yield "," + json.dumps(message) + "\n"
    yield "]"
    thread.join()

@router.post("/api/workflows/stream/{workflow_name}", response_model=None)
def stream_workflow(request: Request, workflow_name: str, workflow_inputs: Optional[List[NodeParameter]]):
    """
    Stream the result of a specific workflow with the given inputs.

    Args:
        workflow_name (str): The name of the workflow to run.
        workflow_inputs (Dict[str, Any]): The inputs to pass to the workflow.

    Returns:
        StreamingResponse: The result of the workflow execution.

    Raises:
        HTTPException: If the workflow is not found or if there's an error during execution.

    Example:
        To stream the result of 'example_workflow':

        ```
        GET /api/workflows/stream/example_workflow
        {
            "x": 5,
            "y": 3
        }
        ```
    """

    pui: PipelineUI = request.app.state.pui

    if workflow_name not in pui.workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")

    workflow = pui.workflows[workflow_name]

    return StreamingResponse(
        generate_stream(workflow.func, pui),
        media_type='text/plain'
    )

@router.post("/api/run_workflow/{workflow_name}")
async def run_workflow(request: Request, workflow_name: str, workflow_inputs: Optional[Dict[str, Any]] = None):
    """
    USED for replicate like interfaces.
    Run a specific workflow with the given inputs. The output will be parsed into artifacts 

    Args:
        workflow_name (str): The name of the workflow to run.
        workflow_inputs (Dict[str, Any]): The inputs to pass to the workflow.

    Returns:
        dict: The last message from the workflow execution stream.

    Raises:
        HTTPException: If the workflow is not found or if there's an error during execution.

    Example:
        To run the 'example_workflow':

        ```
        POST /api/run_workflow/example_workflow
        {
            "x": 5,
            "y": 3
        }
        ```

        Response:
        ```
        {
            "name": "example_workflow",
            "status": "completed",
            "func_type": "workflow", 
            "duration": "1.23s",
            "artifact_id": "...",
            "artifact_url": "..."
        }
        ```
    """
    pui: PipelineUI = request.app.state.pui

    if workflow_name not in pui.workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")

    workflow = pui.workflows[workflow_name]
    func = workflow.func

    # Execute workflow to generate stream
    if workflow_inputs:
        result = func(**workflow_inputs)
    else:
        result = func()

    # Get messages from queue until workflow completion
    last_message = None
    while True:
        message = pui.stream_state_manager.output_queue.get()
        last_message = message
        if message.get("func_type") == "workflow" and message.get("status") == "completed":
            break

    return last_message