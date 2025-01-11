from typing import Dict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from pipeline_ui.modules.pui.pui import PipelineUI

router = APIRouter()


def generate_openapi_schema(pui: PipelineUI) -> Dict:
    openapi_schema = {
        "openapi": "3.0.2",
        "info": {
            "title": "PipelineUI Node API",
            "version": "1.0.0",
        },
        "paths": {},
    }

    for node_name, node in pui.nodes.items():
        path = f"/api/run/{node_name}"
        openapi_schema["paths"][path] = {
            "post": {
                "summary": f"Run {node_name}",
                "operationId": f"run_{node_name}",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "args": {
                                        "type": "object",
                                        "properties": {
                                            input.name: {"type": input.python_type.lower()} for input in node.inputs
                                        },
                                        "required": [input.name for input in node.inputs],
                                    }
                                },
                                "required": ["args"],
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        output.name: {"type": output.python_type.lower()} for output in node.outputs
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"detail": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Function not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"detail": {"type": "string"}},
                                }
                            }
                        },
                    },
                },
            }
        }

    return openapi_schema


@router.get("/pui-docs", response_class=HTMLResponse)
async def get_openapi_docs(request: Request):
    pui: PipelineUI = request.app.state.pui
    openapi_schema = generate_openapi_schema(pui)

    swagger_ui_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PipelineUI Node API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
            const ui = SwaggerUIBundle({{
                spec: {openapi_schema},
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                deepLinking: true
            }})
        </script>
    </body>
    </html>
    """

    return swagger_ui_html
