from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pvmlib.schemas.success_schema import ResponseMetaSchema, ResponseGeneralSchema
from pvmlib.schemas.errors_schema import ErrorGeneralSchema, ErrorDataSchema, ErrorMetaSchema
from pvmlib.code_diccionary import HTTP_STATUS_CODE
import json
from datetime import datetime
import uuid

class AddDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "healthcheck" in request.url.path:
            return await call_next(request)

        start_time = datetime.now()
        
        response = await call_next(request)
        time_elapsed = (datetime.now() - start_time).total_seconds() * 1000
        response_body = [section async for section in response.__dict__['body_iterator']]
        response_body = json.loads(response_body[0].decode())
        status_message = HTTP_STATUS_CODE.get(response.status_code, "Unknown Status Code")

        type = response_body.get("type", 0)
        message = response_body.get("message", status_message)
        code = response_body.get("code", 0)

        response_body.pop("type", None)
        response_body.pop("message", None)
        response_body.pop("code", None)

        new_response_body = ResponseGeneralSchema(
            type=type,
            message=message,
            code=code,
            data=response_body,
            meta=ResponseMetaSchema(
                id_transaction=uuid.uuid4(),
                status=status_message,
                time_elapsed=time_elapsed
            )
        )

        return JSONResponse(content=new_response_body.model_dump(), status_code=response.status_code)