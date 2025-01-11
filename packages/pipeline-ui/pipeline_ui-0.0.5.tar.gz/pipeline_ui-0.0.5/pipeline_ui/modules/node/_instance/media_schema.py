from pipeline_ui.modules.node._instance.base_schema import BaseNodeInputInstance
from pipeline_ui.modules.node._instance.common_schema import ParameterInstance

from pydantic import BaseModel

class ImageInputInstance(BaseNodeInputInstance):
    python_type: str = "Image"
    render: bool = False

class FileInputInstance(BaseNodeInputInstance):
    python_type: str = "File"
    render: bool = False

class VideoInputInstance(BaseNodeInputInstance):
    python_type: str = "Video"
    render: bool = False

class AudioInputInstance(BaseNodeInputInstance):
    python_type: str = "Audio"
    render: bool = False

MediaInputInstance = ImageInputInstance | FileInputInstance | VideoInputInstance | AudioInputInstance

class MediaParameterInstance(BaseModel):
    description: str
    parameter_type: str = 'filepicker'

class ImageParameterInstance(MediaParameterInstance):
    python_type: str = "Image"


class FileParameterInstance(MediaParameterInstance):
    python_type: str = "File"


class VideoParameterInstance(MediaParameterInstance):
    python_type: str = "Video"

class AudioParameterInstance(MediaParameterInstance):
    python_type: str = "Audio"

MediaParameterInstanceType = ImageParameterInstance | FileParameterInstance | VideoParameterInstance | AudioParameterInstance