from litestar.exceptions import HTTPException, ValidationException
from error import BaseError
from error.handler import ErrorHandler

_handler = ErrorHandler()


exception_handlers = {
    BaseError: _handler.base_handler,
    ValidationException: _handler.validation_handler,
    HTTPException: _handler.http_handler,
    Exception: _handler.base_handler,
}
