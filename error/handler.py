import logging
import traceback
from typing import Any
from litestar import Request, Response
from litestar.exceptions import HTTPException, ValidationException
from litestar.response import File
from error import BaseError
from middlewares.lang import DEFAULT_LANG, resolve_message
from utils import get_project_root
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


logger = logging.getLogger("PW-Admin-Backend")

ERROR_PAGES = {
    HTTP_404_NOT_FOUND: "not_found.html",
    HTTP_500_INTERNAL_SERVER_ERROR: "internal_server_error.html",
}


def resolve_lang(request: Request) -> str:
    return getattr(request.state, "lang", DEFAULT_LANG)


def wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")

def render(request: Request, status_code: int, message: str, error: dict[str, Any] | None = None) -> Response:
    page = ERROR_PAGES.get(status_code)
    if page and wants_html(request):
        return File(
            path=get_project_root() / "static" / "page" / page,
            status_code=status_code,
            media_type="text/html",
            content_disposition_type="inline",
        )
    return Response(status_code=status_code, content={"message": message, "error": error})


class ErrorHandler:
    def base_handler(self, request: Request, exc: Exception) -> Response:
        if isinstance(exc, BaseError):
            lang = resolve_lang(request)
            error = (
                {field: [resolve_message(m, lang) for m in msgs] for field, msgs in exc.error.items()}
                if exc.error
                else exc.error
            )
            return render(request, exc.status_code, resolve_message(exc.message, lang), error)

        logger.error(traceback.format_exc())
        return render(
            request,
            HTTP_500_INTERNAL_SERVER_ERROR,
            resolve_message("internal_server_error", resolve_lang(request)),
        )

    def validation_handler(self, request: Request, exc: ValidationException) -> Response:
        error: dict[str, Any] = {}
        for item in exc.extra or []:
            if isinstance(item, dict):
                error.setdefault(item.get("key") or "body", []).append(item.get("message", exc.detail))
            else:
                error.setdefault("body", []).append(str(item))

        return render(
            request,
            HTTP_422_UNPROCESSABLE_ENTITY,
            resolve_message("data_validation_error", resolve_lang(request)),
            error or None,
        )

    def http_handler(self, request: Request, exc: HTTPException) -> Response:
        lang = resolve_lang(request)
        message = exc.detail
        if exc.status_code == HTTP_404_NOT_FOUND:
            message = resolve_message("data_not_found_error", lang)
        elif exc.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            message = resolve_message("internal_server_error", lang)
        return render(request, exc.status_code, message, getattr(exc, "extra", None) or None)
