from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from ..utils import Utils
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_405_METHOD_NOT_ALLOWED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from pvmlib.schemas.errors_schema import ErrorGeneralSchema, ErrorDataSchema, ErrorMetaSchema
from fastapi.responses import JSONResponse

class ErrorResponse(Exception):
    def __init__(
            self, error_code: str, message: str, transaction_id: str,
            status_code: int = 500, info: str = None,
            reference_code: str = None, **kwargs
        ) -> None:
        self._status_code = status_code
        self.data = {
            "user_message": message
        }
        self.meta = {
            "error_code": int(error_code),
            "transaction_id": transaction_id,
            "info": info,
            "reference_code": reference_code,
            **kwargs
        }

async def error_exception(exc: Exception):
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="An unexpected error occurred."),
        trace=ErrorMetaSchema(
            error_code=500,
            info=str(exc.__traceback__)
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=500)


async def internal_server_error_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="An unexpected error occurred."),
        trace=ErrorMetaSchema(
            error_code=HTTP_500_INTERNAL_SERVER_ERROR,
            info=str(exc.detail) if exc.detail else "Internal Server Error"
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=HTTP_500_INTERNAL_SERVER_ERROR)

async def error_exception_handler(request: Request, exc: HTTPException):
    status_code = getattr(exc, 'status_code', HTTP_500_INTERNAL_SERVER_ERROR)
    detail = getattr(exc, 'detail', "An unexpected error occurred.")
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message=detail),
        trace=ErrorMetaSchema(
            error_code=status_code,
            info=str(detail)
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=status_code)

async def not_found_error_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="Resource not found."),
        trace=ErrorMetaSchema(
            error_code=exc.status_code,
            info=exc.detail
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=exc.status_code)

async def parameter_exception_handler(request: Request, exc: RequestValidationError):
    error_details = Utils.get_error_details(exc.errors())
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="Validation error."),
        trace=ErrorMetaSchema(
            error_code=HTTP_422_UNPROCESSABLE_ENTITY,
            info="; ".join(error_details)
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=HTTP_422_UNPROCESSABLE_ENTITY)

async def method_not_allowed_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="Method not allowed."),
        trace=ErrorMetaSchema(
            error_code=HTTP_405_METHOD_NOT_ALLOWED,
            info=str(exc.detail) if exc.detail else "Method Not Allowed"
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=HTTP_405_METHOD_NOT_ALLOWED)

async def bad_request_exception_handler(request: Request, exc: HTTPException):
    error_response = ErrorGeneralSchema(
        error=ErrorDataSchema(user_message="Bad request."),
        trace=ErrorMetaSchema(
            error_code=HTTP_400_BAD_REQUEST,
            info=exc.detail
        )
    )
    return JSONResponse(content=error_response.model_dump(), status_code=HTTP_400_BAD_REQUEST)