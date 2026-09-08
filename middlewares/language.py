from litestar.datastructures import Headers
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from middlewares.lang import DEFAULT_LANG, SUPPORTED_LANGUAGES, current_lang


class LanguageMiddleware(ASGIMiddleware):
    """Resolves the request language from `Accept-Language` onto both
    `scope["state"]["lang"]` (read by the exception handlers) and the `current_lang`
    contextvar (read by `schemas.response.Response` to localize its default success
    message). Falls back to `DEFAULT_LANG` for anything unsupported."""

    scopes = (ScopeType.HTTP,)

    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        raw = Headers.from_scope(scope).get("Accept-Language", "")
        lang = raw.split(",")[0].split(";")[0].strip().lower().split("-")[0]
        lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANG

        scope["state"]["lang"] = lang
        token = current_lang.set(lang)
        try:
            await next_app(scope, receive, send)
        finally:
            current_lang.reset(token)
