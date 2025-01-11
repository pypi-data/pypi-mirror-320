from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from pipeline_ui.modules.node.schema.node_schema import NodeInputInstance, NodeOutputInstance, NodeSchema, ParameterInstanceType
from pipeline_ui.modules.workflow.schema.client.schema import NodePosition


# Base models for edge components
class EdgeSource(BaseModel):
    node: str
    output: str = "output"  # Default output name
    node_index: Optional[int] = None


class EdgeTarget(BaseModel):
    node: str
    input: str
    node_index: Optional[int] = None



class WorkflowEdge(BaseModel):
    source: EdgeSource
    target: EdgeTarget


class WorkflowStep(BaseModel):
    function: str
    args: Dict[str, Any]


class Workflow(BaseModel):
    steps: List[WorkflowStep]


class WorkflowSchema(BaseModel):
    name: str
    description: Optional[str] = None
    pack_id: Optional[str] = None
    source_code: Optional[str] = None
    input_parameters: List[ParameterInstanceType]
    outputs: List[NodeOutputInstance]
    nodes: List[NodeSchema]
    edges: List[WorkflowEdge]
    positions: Optional[List[NodePosition]] = None

    class Config:
        exclude_none = True

    

class NodeParameter(BaseModel):
    node_name: str
    node_index: Optional[int] = None
    parameter_name: str
    parameter_value: str