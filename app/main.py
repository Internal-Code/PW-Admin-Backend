from litestar import Litestar
from litestar.plugins.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from app.controller.common import CommonController
from config.openapi import openapi_config
from config.setting import get_settings
from error.register import exception_handlers
from utils.log import logging_config
from middlewares.error_page import ErrorPageMiddleware
from middlewares.language import LanguageMiddleware
from service.otel import setup_telemetry, shutdown_telemetry
from service.redis import close_redis

settings = get_settings()
setup_telemetry()


async def _on_shutdown(_app: Litestar) -> None:
    await close_redis()
    shutdown_telemetry()

app = Litestar(
    route_handlers=[
        CommonController,
    ],
    plugins=[OpenTelemetryPlugin(OpenTelemetryConfig(exclude=["schema", "docs"]))],
    middleware=[ErrorPageMiddleware(), LanguageMiddleware()],
    exception_handlers=exception_handlers,
    openapi_config=openapi_config,
    logging_config=logging_config,
    on_shutdown=[_on_shutdown],
)
