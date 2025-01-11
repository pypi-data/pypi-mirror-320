from pydantic_settings import BaseSettings
from typing import Callable


class Settings(BaseSettings):
    # MONGO
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "default_db"
    MONGO_TIMEOUT_MS: int = 500
    MONGO_MAX_POOL_SIZE: int = 20
    # APP
    APP_NAME: str = "default_app"
    SERVICE_NAME: str = "default_service"
    NAMESPACE: str = "default_namespace"
    API_VERSION: str = "v1"
    ENABLE_DOCS: bool = False
    # LOGS
    VERSION_LOG: str = "1.0.0"
    #SESSION
    IGNORE_SESSION: bool = False
    #EXTRA SETTINGS
    ENV: str = "DEV"
    HTTP_PORT: int = 8080
    RETRY: int = 3
    TIME_CLOSE_CIRCUIT: int = 5
    MAX_ATTEMPTS_OPEN_CIRCUIT: int = 10
    MAX_TRYING_TRANSACTIONS: int = 3
    URL_BASE: str = "http//localhost:8080/puntodeventa/api/v1"

    class Config:
        env_file = ".env"
        @classmethod
        def parse_env_var(cls, field: str, value: str) -> list:
            return value.split(',')


def _configure_initial_settings() -> Callable[[], Settings]:
    settings = Settings()

    def get_settings() -> Settings:
        return settings

    return get_settings


get_settings = _configure_initial_settings()