from typing import Optional

from PIL import Image

from pipeline_ui.modules.node._parameter.base_schema import Parameter


class ImageParameter(Parameter):
    def __new__(cls, description: Optional[str] = None) -> Image.Image:
        return Image.new("RGB", (100, 100))

class AudioParameter(Parameter):
    def __new__(cls, description: Optional[str] = None) -> str:
        return "audio"

class VideoParameter(Parameter):
    def __new__(cls, description: Optional[str] = None) -> str:
        return "video"

class FileParameter(Parameter):
    def __new__(cls, description: Optional[str] = None) -> str:
        return "file"
    
MediaParameterType = ImageParameter | AudioParameter | VideoParameter | FileParameter