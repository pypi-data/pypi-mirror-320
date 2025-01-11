from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pvmlib.schemas.success_schema import ResponseGeneralSchema, ResponseMetaSchema
from pvmlib.schemas.errors_schema import ErrorGeneralSchema, ErrorDataSchema, ErrorMetaSchema
from pvmlib.code_diccionary import HTTP_STATUS_CODE
import json
from datetime import datetime
import uuid

class AddDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "healthcheck" in request.url.path:
            return await call_next(request)

        if "id_transaction" not in request.headers:
            error_response = ErrorGeneralSchema(
                error=ErrorDataSchema(user_message="id_transaction is required"),
                trace=ErrorMetaSchema(
                    error_code=400,
                    info="BadRequest"
                )
            )
            return JSONResponse(content=error_response.model_dump(), status_code=400)

        start_time = datetime.now()
        
        response = await call_next(request)
        time_elapsed = (datetime.now() - start_time).total_seconds() * 1000
        response_body = [section async for section in response.__dict__['body_iterator']]
        response_body = json.loads(response_body[0].decode())

        # Remove type, message, and code from response_body if they exist
        response_body.pop("type", None)
        response_body.pop("message", None)
        response_body.pop("code", None)

        status_message = HTTP_STATUS_CODE.get(response.status_code, "Unknown Status Code")
        new_response_body = ResponseGeneralSchema(
            type=response_body.get("type", 0),
            message=response_body.get("message", "OK"),
            code=response_body.get("code", 0),
            data=response_body,
            meta=ResponseMetaSchema(
                id_transaction=str(uuid.uuid4()),  # Convert UUID to string
                status=status_message,
                time_elapsed=time_elapsed
            )
        )

        return JSONResponse(content=new_response_body.model_dump(), status_code=response.status_code)