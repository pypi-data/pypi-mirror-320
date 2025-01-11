from enum import Enum
from typing import Optional

from pydantic import BaseModel


class NodePosition(BaseModel):
    x: int
    y: int
    node: str | Enum
    index: Optional[int] = None