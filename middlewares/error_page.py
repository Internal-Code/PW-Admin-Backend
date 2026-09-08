import msgspec
from litestar.datastructures import Headers, MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from middlewares.lang import DEFAULT_LANG, resolve_message
from utils import get_project_root

HTML_PAGES = {
    HTTP_404_NOT_FOUND: (get_project_root() / "static" / "page" / "not_found.html").read_bytes(),
    HTTP_500_INTERNAL_SERVER_ERROR: (get_project_root() / "static" / "page" / "internal_server_error.html").read_bytes(),
}
MESSAGE_KEYS = {
    HTTP_404_NOT_FOUND: "data_not_found_error",
    HTTP_500_INTERNAL_SERVER_ERROR: "internal_server_error",
}


class ErrorPageMiddleware(ASGIMiddleware):
    scopes = (ScopeType.HTTP,)
    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        wants_html = "text/html" in Headers.from_scope(scope).get("accept", "")

        replacement: bytes | None = None
        body_sent = False

        async def wrapped_send(message: Message) -> None:
            nonlocal replacement, body_sent

            if message["type"] == "http.response.start":
                status = message["status"]
                if status in HTML_PAGES:
                    if wants_html:
                        replacement = HTML_PAGES[status]
                        content_type = "text/html; charset=utf-8"
                    else:
                        lang = scope.get("state", {}).get("lang", DEFAULT_LANG)
                        replacement = msgspec.json.encode(
                            {"message": resolve_message(MESSAGE_KEYS[status], lang), "error": None}
                        )
                        content_type = "application/json"

                    headers = MutableScopeHeaders.from_message(message)
                    headers["content-type"] = content_type
                    headers["content-length"] = str(len(replacement))
                    if "content-disposition" in headers:
                        del headers["content-disposition"]
                await send(message)
                return

            if message["type"] == "http.response.body":
                if replacement is None:
                    await send(message)
                    return
                if not body_sent:
                    body_sent = True
                    await send({"type": "http.response.body", "body": replacement, "more_body": False})
                return

            await send(message)

        await next_app(scope, receive, wrapped_send)
