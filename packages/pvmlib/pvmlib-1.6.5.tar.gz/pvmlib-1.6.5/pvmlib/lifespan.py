from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import database_manager
from .settings import get_settings
from .logs.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()
setting_env = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
        try:
            if "MONGO_URI" in setting_env.model_fields:
                await database_manager.connect_to_mongo(settings_env=setting_env)
                logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Error in connect to MongoDB: {e}")
            raise e

        yield
        # Shutdown
        if "MONGO_URI" in setting_env:
            logger.info("Disconnecting from MongoDB")
            await database_manager.disconnect_from_mongo()