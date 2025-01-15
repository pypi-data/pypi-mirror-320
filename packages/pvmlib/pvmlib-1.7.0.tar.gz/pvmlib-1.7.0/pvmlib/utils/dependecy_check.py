from typing import List, Dict, Callable
from fastapi import HTTPException
from pvmlib.logs import LoggerSingleton
from pvmlib.database import DatabaseManager
import httpx
from urllib.parse import urlparse

logger = LoggerSingleton().get_logger()

class DependencyChecker:
    def __init__(self, dependencies: List[Callable[[], Dict[str, str]]]):
        self.dependencies = dependencies

    async def check_dependencies(self) -> Dict[str, str]:
        results = {}
        for check in self.dependencies:
            try:
                result = await check()
                results.update(result)
            except Exception as e:
                logger.error(f"Dependency check failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Dependency check failed: {str(e)}")
        return results

async def check_mongo(database_manager: DatabaseManager) -> Dict[str, str]:
    try:
        # Verificar si ya hay una conexión existente
        if not database_manager.mongo_client:
            await database_manager.connect_to_mongo()
        
        await database_manager.mongo_database.command("ping")
        logger.info("MongoDB ping successful")
        return {"mongodb": "UP"}
    except Exception as e:
        logger.error(f"MongoDB ping failed: {str(e)}")
        return {"mongodb": "DOWN"}

async def check_external_service(url: str) -> Dict[str, str]:
    parsed_url = urlparse(url)
    service_name = parsed_url.netloc.split('.')[0]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"External service {service_name} is UP")
                return {service_name: "UP"}
            else:
                logger.error(f"External service {service_name} is DOWN")
                return {service_name: "DOWN"}
    except Exception as e:
        logger.error(f"External service {service_name} check failed: {str(e)}")
        return {service_name: "DOWN"}