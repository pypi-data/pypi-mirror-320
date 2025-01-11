from contextlib import contextmanager
import abc
import motor.motor_asyncio
from pvmlib.logger import LoggerSingleton
from tenacity import retry, stop_after_attempt, wait_fixed

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
    async def connect_to_mongo(self, settings_env):
        try:
            self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings_env.MONGO_URI)
            self.mongo_database = self.mongo_client[settings_env.MONGO_DB_NAME]
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect_from_mongo(self):
        self.mongo_client.close()

    @contextmanager
    def session(self):
        try:
            yield self.mongo_database
        finally:
            pass 

database_manager = DatabaseManager()