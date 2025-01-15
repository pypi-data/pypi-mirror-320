from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ApplicationSchema(BaseModel):
    name: str = Field(
        ...,
        title="Application Name",
        description="Name of the application"
    )
    version: str = Field(
        ...,
        title="Application Version",
        description="Version of the application"
    )
    env: str = Field(
        ...,
        title="Environment",
        description="Environment where the application is running"
    )
    kind: str = Field(
        ...,
        title="Kind",
        description="Kind of the application"
    )

class MeasurementSchema(BaseModel):
    method: str = Field(
        ...,
        title="Method",
        description="HTTP method used in the request"
    )
    elapsedTime: int = Field(
        ...,
        title="Elapsed Time",
        description="Time elapsed for the request in milliseconds"
    )
    status: Optional[str] = Field(
        None,
        title="Status",
        description="Status of the measurement"
    )

class DefaultLoggerSchema(BaseModel):
    level: str = Field(
        ...,
        title="Log Level",
        description="Level of the log (e.g., INFO, ERROR)"
    )
    schemaVersion: str = Field(
        ...,
        title="Schema Version",
        description="Version of the log schema"
    )
    logType: str = Field(
        ...,
        title="Log Type",
        description="Type of the log (e.g., TRANSACTION)"
    )
    sourceIP: str = Field(
        ...,
        title="Source IP",
        description="IP address of the source"
    )
    status: str = Field(
        ...,
        title="Status",
        description="Status of the log (e.g., SUCCESS, FAILURE)"
    )
    message: str = Field(
        ...,
        title="Message",
        description="Message of the log"
    )
    logOrigin: str = Field(
        ...,
        title="Log Origin",
        description="Origin of the log (e.g., INTERNAL)"
    )
    timestamp: str = Field(
        ...,
        title="Timestamp",
        description="Timestamp of the log"
    )
    tracingId: str = Field(
        ...,
        title="Tracing ID",
        description="Tracing ID for the log"
    )
    hostname: str = Field(
        ...,
        title="Hostname",
        description="Hostname where the log was generated"
    )
    eventType: str = Field(
        ...,
        title="Event Type",
        description="Type of the event"
    )
    application: ApplicationSchema = Field(
        ...,
        title="Application",
        description="Application information"
    )
    measurement: MeasurementSchema = Field(
        ...,
        title="Measurement",
        description="Measurement information"
    )
    destinationIP: str = Field(
        ...,
        title="Destination IP",
        description="IP address of the destination"
    )
    additionalInfo: Optional[Dict[str, Any]] = Field(
        None,
        title="Additional Info",
        description="Additional information for the log"
    )

logs_schema = {
    "definitions": {
        "ApplicationSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "env": {"type": "string"},
                "kind": {"type": "string"}
            }
        },
        "MeasurementSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string"},
                "elapsedTime": {"type": "integer"},
                "status": {"type": "string"}
            }
        },
        "DefaultLoggerSchema": {
            "type": "object",
            "properties": {
                "level": {"type": "string"},
                "schemaVersion": {"type": "string"},
                "logType": {"type": "string"},
                "sourceIP": {"type": "string"},
                "status": {"type": "string"},
                "message": {"type": "string"},
                "logOrigin": {"type": "string"},
                "timestamp": {"type": "string"},
                "tracingId": {"type": "string"},
                "hostname": {"type": "string"},
                "eventType": {"type": "string"},
                "application": {"$ref": "#/definitions/ApplicationSchema"},
                "measurement": {"$ref": "#/definitions/MeasurementSchema"},
                "destinationIP": {"type": "string"},
                "additionalInfo": {"type": "object"}
            }
        }
    }
}
