from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from ..logger import LoggerSingleton
from datetime import datetime
from ..logs.measurement import Measurement
from ..logs.application import Application
from pvmlib.schemas.errors_schema import ErrorGeneralSchema, ErrorDataSchema, ErrorMetaSchema
from fastapi.responses import JSONResponse




class InterceptMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_info: Application, auth_service_url: str = None):
        super().__init__(app)
        self.app_info = app_info
        self.logger = LoggerSingleton().get_logger()
        self.auth_service_url = auth_service_url

    async def dispatch(self, request: Request, call_next):
        if "healthcheck" in request.url.path:
            return await call_next(request)

        start_time = datetime.now()
        
        measurement = Measurement(
            service=self.app_info.name,
            method=request.method,
            message="Success",
            time_elapsed=0
        )

        response = None
        
        try:
            response = await call_next(request)
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            measurement.time_elapsed = int(elapsed_time)
            measurement.message = "success"
            self.logger.info(f"Request processed successfully: {request.url.path}", extra={"measurement": measurement})
            return response
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            measurement.time_elapsed = int(elapsed_time)
            measurement.message = "error"
            self.logger.error(f"Request failed: {request.url.path}", exc_info={str(e)}, extra={"measurement": measurement})
            
            error_response = ErrorGeneralSchema(
                error=ErrorDataSchema(user_message="An unexpected error occurred."),
                trace=ErrorMetaSchema(
                    error_code=500,
                    info=str(e)
                )
            )
            
            return JSONResponse(content=error_response.model_dump(), status_code=500)