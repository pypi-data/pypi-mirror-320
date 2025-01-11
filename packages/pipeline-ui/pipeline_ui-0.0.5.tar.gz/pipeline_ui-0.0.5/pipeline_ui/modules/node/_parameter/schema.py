from pipeline_ui.modules.node._parameter.base_schema import BaseParameterType
from pipeline_ui.modules.node._parameter.media_schema import MediaParameterType

ParameterType = BaseParameterType | MediaParameterType