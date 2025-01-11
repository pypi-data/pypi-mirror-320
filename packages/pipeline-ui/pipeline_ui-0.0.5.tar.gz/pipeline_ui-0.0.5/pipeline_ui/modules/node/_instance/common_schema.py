from typing import List, Literal, Optional, TypeAlias, Union

from pydantic import BaseModel

InputControlType: TypeAlias = Literal["select", "slider", "text"]

class ParameterInstance(BaseModel):
    name: str
    description: Optional[str] = None
    python_type: str  # Allow any type, will be converted to string in model_dump

    parameter_type: (
        InputControlType  # must be implemented in the subclass (TODO should find a way to enforce this with validation)
    )


class NumberParameterInstance(ParameterInstance):
    default: Optional[Union[int, float]] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    parameter_type: InputControlType = "slider"


class TextParameterInstance(ParameterInstance):
    default: str
    parameter_type: InputControlType = "text"
    python_type: str = "string"

class RadioParameterInstance(ParameterInstance):
    options: List[str]
    default: str
    parameter_type: InputControlType = "select"
    python_type: str = "string"

BaseParameterInstanceType = NumberParameterInstance | RadioParameterInstance | TextParameterInstance