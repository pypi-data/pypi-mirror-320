from .application import Application
from .measurement import Measurement
from typing import Dict, Any

class DefaultLogger(object):
 
    def __init__(
            self, 
            level: str, 
            schemaVersion: str,
            logType: str,
            sourceIP: str,
            status: str,
            message: str,
            logOrigin: str,
            timestamp: str,
            tracingId: str,
            hostname: str,
            eventType: str,
            application: Application,
            measurement: Measurement,
            destinationIP: str,
            additionalInfo: Dict[str, Any]) -> None:

        self.level = level
        self.schemaVersion = schemaVersion
        self.logType = logType
        self.sourceIP = sourceIP
        self.status = status
        self.message = message
        self.logOrigin = logOrigin
        self.timestamp = timestamp
        self.tracingId = tracingId
        self.hostname = hostname
        self.eventType = eventType
        self.application = application
        self.measurement = measurement
        self.destinationIP = destinationIP
        self.additionalInfo = additionalInfo
    
    def get_default_log(self) -> dict:
        return {
           "level": self.level,
           "schemaVersion": self.schemaVersion,
           "logType": self.logType,
           "sourceIP": self.sourceIP,
           "status": self.status,
           "message": self.message,
           "logOrigin": self.logOrigin,
           "timestamp": self.timestamp,
           "tracingId": self.tracingId,
           "hostname": self.hostname,
           "eventType": self.eventType,
           "application": self.application.get_info_application(),
           "measurement": self.measurement.get_service(),
           "destinationIP": self.destinationIP, 
           "additionalInfo": self.additionalInfo
        }