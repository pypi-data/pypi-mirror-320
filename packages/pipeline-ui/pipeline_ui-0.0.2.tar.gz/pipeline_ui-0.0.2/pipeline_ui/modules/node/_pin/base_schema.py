from typing import Generic, Literal, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T')

class NodeInput(Generic[T]):
    def __new__(
        cls,
        python_type: Type[T],
        description: Optional[str] = None,
    ) -> Type[T]:
        # Return the type itself without instantiating
        return python_type
        
class NodeOutput(BaseModel):
    name: str
    description: Optional[str] = None

class TextOutput(NodeOutput):
    name: Literal["text"] = "text"
