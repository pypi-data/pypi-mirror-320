from typing import Optional

from pydantic import BaseModel


class BaseNodeInputInstance(BaseModel):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    description: Optional[str] = None
    python_type: str  # Allow any type, will be converted to string in model_dump
    color: str = "purple"


class NodeOutputInstance(BaseModel):
    name: str
    description: Optional[str] = None
    python_type: str  # Allow any type, will be converted to string in model_dump
    color: str = "orange"