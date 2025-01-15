import abc
import os
import motor.motor_asyncio

from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_fixed
from pvmlib.logs.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()


class Session:
    pass

class Database:
    @abc.abstractmethod
    @contextmanager
    def session(self): pass

class DatabaseManager(Database):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mongo_database = None
            self.mongo_client = None
            self.initialized = True

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def connect_to_mongo(self):
        try:
            mongo_uri = os.getenv("MONGO_URI", "localhost:27017")
            mongo_timeout_ms = os.getenv("MONGO_TIMEOUT_MS", "5000")
            mongo_max_pool_size =  os.getenv("MONGO_MAX_POOL_SIZE", "100")
            mongo_db_name = os.getenv("MONGO_DB_NAME")

            if not mongo_uri or not mongo_db_name:
                raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in environment variables")

            self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_uri,
                serverSelectionTimeoutMS=int(mongo_timeout_ms),
                maxPoolSize=int(mongo_max_pool_size)
            )
            self.mongo_database = self.mongo_client[mongo_db_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect_from_mongo(self):
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("Disconnected from MongoDB")

    @contextmanager
    def session(self):
        try:
            yield self.mongo_database
        finally:
            pass 

database_manager = DatabaseManager()