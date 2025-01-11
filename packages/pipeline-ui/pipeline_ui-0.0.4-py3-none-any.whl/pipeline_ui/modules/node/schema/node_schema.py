from typing import Dict, List, Optional

from pydantic import BaseModel

from pipeline_ui.modules.common_parser.function_parser_extractor import FunctionInfo
from pipeline_ui.modules.node._instance.base_schema import NodeOutputInstance
from pipeline_ui.modules.node._instance.parameter.schema import ParameterInstanceType
from pipeline_ui.modules.node._instance.schema import NodeInputInstance


class NodeSchema(BaseModel):
    name: str
    func_name: str
    description: str = ""
    docstring: Optional[str] = None
    inputs: List[NodeInputInstance]
    outputs: List[NodeOutputInstance]
    parameters: List[ParameterInstanceType]
    function_info: Dict[str, FunctionInfo]
    pack_id: Optional[str] = None
    source_code: Optional[str] = None

    class Config:
        exclude_none = True
