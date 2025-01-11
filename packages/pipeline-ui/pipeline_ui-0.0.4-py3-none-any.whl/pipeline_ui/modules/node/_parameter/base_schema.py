from typing import Generic, List, Optional, TypeVar, Union, overload

N = TypeVar('N', int, float)

class Parameter:
    """Base class for all parameters"""
    description: Optional[str]
    
    def __init__(self, description: Optional[str] = None):
        self.description = description

class NumberParameter(Parameter, Generic[N]):
    @overload
    def __new__(
        cls,
        default: int,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        description: Optional[str] = None
    ) -> int: ...
    
    @overload
    def __new__(
        cls,
        default: float,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        description: Optional[str] = None
    ) -> float: ...
    
    def __new__(
        cls,
        default: Union[int, float],
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        description: Optional[str] = None
    ) -> Union[int, float]:
        # Determine the type
        default_type = type(default)
        
        # Validation
        if not isinstance(default, (int, float)):
            raise ValueError(f"default must be a number (int or float), got {type(default)}")
        
        # Convert min/max to the same type as default if they exist
        if min is not None:
            min = default_type(min)
        if max is not None:
            max = default_type(max)
            
        # Validation
        if min is not None and default < min:
            raise ValueError(f"default {default} is less than minimum {min}")
        if max is not None and default > max:
            raise ValueError(f"default {default} is greater than maximum {max}")
        
        # Return the default as the correct type
        return default_type(default)
    
class RadioParameter(Parameter):
    def __new__(
        cls,
        default: str,
        options: List[str],
        description: Optional[str] = None
    ) -> str: 
        return default


class TextParameter(Parameter):
    def __new__(
        cls,
        default: str,
        description: Optional[str] = None
    ) -> str:
        return default
    
BaseParameterType = NumberParameter | RadioParameter | TextParameter