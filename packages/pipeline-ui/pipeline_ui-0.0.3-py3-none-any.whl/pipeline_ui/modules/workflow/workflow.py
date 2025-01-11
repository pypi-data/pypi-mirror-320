import base64
import inspect
import json
import pickle
from typing import Any, Callable, Dict, List, Optional

from pipeline_ui.modules.common_parser.full_code_extractor import get_full_code_for_workflow
from pipeline_ui.modules.common_parser.function_parser_extractor import extract_function_code_recursive, FunctionInfo   
from pipeline_ui.modules.node.parser.parameter_parser import get_parameters
import requests

from pipeline_ui.modules.auth.auth import load_access_token
from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.node.schema.node_schema import NodeSchema
from pipeline_ui.modules.workflow.parser.argument_parser import parse_values
from pipeline_ui.modules.workflow.parser.edge_parser import extract_edges_from_workflow
from pipeline_ui.modules.workflow.parser.parser import extract_nodes
from pipeline_ui.modules.workflow.parser.streaming_parser import get_stream_function
from pipeline_ui.modules.workflow.schema.internal.schema import EdgeSource, EdgeTarget, NodeParameter, NodePosition, WorkflowEdge, WorkflowSchema

from pipeline_ui.modules.node.parser.node_input_parser import get_node_inputs
from pipeline_ui.modules.node.parser.node_output_parser import get_node_outputs

class Workflow:
    def __init__(
        self,
        func: Callable,
        nodes: Dict[str, Node],
        name: Optional[str] = None,
        positions: Optional[List[NodePosition]] = None,
        description: Optional[str] = None,
    ):
        self.name = name or func.__name__
        self.description = description
        # self.edges = extract_edges(func)
        self.nodes: List[NodeSchema] = extract_nodes(func, nodes)
        # self.edges: List[WorkflowEdge] = extract_workflow_edges(func)
        self.func = func
        self.func_name = func.__name__
        self.positions: Optional[List[NodePosition]] = positions
        self.edges : List[WorkflowEdge] = extract_edges_from_workflow(func, self.nodes)
        self.arguments = parse_values(func)
        self.function_info = extract_function_code_recursive(func)
        self.input_parameters = get_parameters(func)
        self.outputs = get_node_outputs(func)

        assert self._check_positions(), "The positions are not valid"

        self.source_code = get_full_code_for_workflow(self.func_name, self.function_info)
        # print("self.source_code", self.source_code)
        # raise Exception("test")

        # pprint.pp(self.edges)
        # self.streaming_func = get_stream_function(func)
        # self.decorator = decorator
        # print("here")
        # self.streaming_func = self.func.stream

    def _check_positions(self):
        if self.positions is not None:
            for position in self.positions:
                if position.node not in [node.name for node in self.nodes]:
                    raise ValueError(f"Node {position.node} not found in the workflow")
        return True

    def __repr__(self):
        return f"Workflow(name: {self.name}, edges: {self.edges}, nodes: {self.nodes})"

    def publish(self):
        url = "http://0.0.0.0:8401/workflows/"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": load_access_token(),
        }
        data = {
            "name": self.name,
            "code": inspect.getsource(self.func),
            "description": self.func.__doc__ or "",
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Node published successfully")
        else:
            print(f"Failed to publish node: {response.status_code} - {response.text}")

    def to_schema(self) -> WorkflowSchema:

        edges = [
            WorkflowEdge(
                source=EdgeSource(node=edge.source.node, output=edge.source.output, node_index=edge.source.node_index),
                target=EdgeTarget(node=edge.target.node, input=edge.target.input, node_index=edge.target.node_index),
            )
            for edge in self.edges
        ]


        return WorkflowSchema(
            name=self.name,
            description=self.description,
            source_code=self.source_code,
            input_parameters=self.input_parameters,
            outputs=self.outputs,
            nodes=self.nodes,
            edges=edges,
            positions=self.positions,
        )

    def to_json(self, published_pack_id: str) -> dict:
        json_data = self.to_schema().model_dump()
        # print("json_data", json_data)
        # raise Exception("test")
        json_data["pack_id"] = published_pack_id
        return json_data