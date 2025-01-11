from motor.motor_asyncio import AsyncIOMotorClient
from ..logs import Measurement
from .mongo_repository import MongoRepository
from datetime import datetime
import time

class MongoWorkerRepository(MongoRepository):

    get_time_elapsed_ms = lambda self, init_time=None, decimals=2: round((time.perf_counter()-init_time)*1000, decimals)

    def __init__(self, database_url: str) -> None:
        self.client = AsyncIOMotorClient(database_url)
        self.database = self.client.get_default_database()

    async def is_up(self, log) -> bool:
        init_time = time.perf_counter()
        try:
            await self.database.command("ping")
            time_elapsed = self.get_time_elapsed_ms(init_time)
            measurement = Measurement("MongoDB", time_elapsed)
            log.info("MongoDB is up", measurement=measurement)
            return True
        except Exception as e:
            time_elapsed = self.get_time_elapsed_ms(init_time)
            measurement = Measurement("MongoDB", time_elapsed, "error")
            log.error("MongoDB is not up", error=str(e), measurement=measurement)
            return False
