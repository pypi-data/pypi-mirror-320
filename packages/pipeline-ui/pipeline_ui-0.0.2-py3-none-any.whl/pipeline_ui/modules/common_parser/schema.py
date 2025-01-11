# from typing import List, Optional
# from pydantic import BaseModel, Field


# class FunctionInfo(BaseModel):
#     """Pydantic model for storing function information"""
#     source_code: str
#     name: str
#     called_functions: List[str] = Field(default_factory=list)

#     docstring: Optional[str] = None
#     module: str
#     line_number: int
#     is_async: bool = False
#     decorators: List[str] = Field(default_factory=list)

    