class Measurement(object):

    def __init__(self, service: str, method: str, time_elapsed: int | float, message: str = "Success") -> None:
        self.service = service
        self.method = method
        self.message = message
        self.time_elapsed = time_elapsed

    def get_service(self) -> dict:
        return {
            "service": self.service,
            "method": self.method,
            "message": self.message,
            "time_elapsed": self.time_elapsed
        }