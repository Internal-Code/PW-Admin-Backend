from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin


openapi_config = OpenAPIConfig(
    title="Will be changed later",
    version="0.1.0",
    description="will be added later..",
    path="/docs",
    render_plugins=[ScalarRenderPlugin(path="/")],
)
