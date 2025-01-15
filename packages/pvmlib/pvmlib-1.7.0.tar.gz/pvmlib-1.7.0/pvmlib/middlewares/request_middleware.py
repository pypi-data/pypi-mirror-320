import uuid
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pvmlib.logs import LoggerSingleton
from datetime import datetime
from pvmlib.schemas.logs_schema import ApplicationSchema, MeasurementSchema

SCHEMA_VERSION = os.getenv("SCHEMA_VERSION", "1.0.0")

class InterceptMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_info: ApplicationSchema):
        super().__init__(app)
        self.app_info = app_info
        self.logger = LoggerSingleton().get_logger()

    async def dispatch(self, request: Request, call_next):
        if "healthcheck" in request.url.path:
            return await call_next(request)

        start_time = datetime.now()
        measurement = MeasurementSchema(
            status="IN_PROGRESS",
            method=request.method,
            elapsedTime=0
        )

        destination_ip = request.client.host if request.client else "N/A"
        tracing_id = str(uuid.uuid4())
        response = None
        
        try:
            response = await call_next(request)
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            measurement.elapsedTime = int(elapsed_time)
            measurement.status = "SUCCESS"
            
            log_entry = {
                "level": "INFO",
                "schemaVersion": "1.0.0",
                "logType": "TRANSACTION",
                "sourceIP": request.client.host,
                "status": "SUCCESS",
                "message": f"Request processed successfully: {request.url.path}",
                "logOrigin": "INTERNAL",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "tracingId": request.headers.get("PVM-Request-ID", tracing_id),
                "hostname": request.url.hostname,
                "eventType": "REQUEST_PROCESSED",
                "application": self.app_info,
                "measurement": measurement,
                "destinationIP": destination_ip,
                "additionalInfo": {"path": request.url.path}
            }
            self.logger.info(log_entry)
            return response
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            measurement.elapsedTime = int(elapsed_time)
            measurement.status = "FAILURE"
            
            log_entry = {
                "level": "ERROR",
                "schemaVersion": "1.0.0",
                "logType": "TRANSACTION",
                "sourceIP": request.client.host,
                "status": "FAILURE",
                "message": f"Request failed: {request.url.path}",
                "logOrigin": "INTERNAL",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "tracingId": request.headers.get("X-Request-ID", tracing_id),
                "hostname": request.url.hostname,
                "eventType": "REQUEST_FAILED",
                "application": self.app_info,
                "measurement": measurement,
                "destinationIP": destination_ip,
                "additionalInfo": {"path": request.url.path, "error": str(e)}
            }
            self.logger.error(log_entry)
            raise e