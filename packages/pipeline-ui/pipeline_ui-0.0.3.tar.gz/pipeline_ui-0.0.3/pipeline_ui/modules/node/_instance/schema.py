from pipeline_ui.modules.node._instance.base_schema import BaseNodeInputInstance
from pipeline_ui.modules.node._instance.media_schema import MediaInputInstance

NodeInputInstance = MediaInputInstance | BaseNodeInputInstance
