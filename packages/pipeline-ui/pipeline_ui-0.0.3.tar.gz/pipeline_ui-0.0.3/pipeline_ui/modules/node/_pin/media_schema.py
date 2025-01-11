from typing import Literal, Optional

from PIL import Image

from pipeline_ui.modules.node._pin.base_schema import NodeInput, NodeOutput


class ImageInput(NodeInput[Image.Image]):
    def __new__(
        cls,
        description: Optional[str] = None,
        render: bool = False
    ) -> Image.Image:
        return Image.new("RGB", (100, 100))
        
class ImageOutput(NodeOutput):
    name: Literal["image"] = "image"
    render: bool = False

class VideoInput(NodeInput[str]):
    def __new__(
        cls,
        description: Optional[str] = None,
        render: bool = False
    ) -> str:
        return "video"

class VideoOutput(NodeOutput):
    name: Literal["video"] = "video"
    render: bool = False

class AudioInput(NodeInput[str]):
    def __new__(
        cls,
        description: Optional[str] = None,
    ) -> str:
        return "audio"

class AudioOutput(NodeOutput):
    name: Literal["audio"] = "audio"


class FileInput(NodeInput[str]):
    def __new__(
        cls,
        description: Optional[str] = None,
    ) -> str:
        return "file"

class FileOutput(NodeOutput):
    name: Literal["file"] = "file"