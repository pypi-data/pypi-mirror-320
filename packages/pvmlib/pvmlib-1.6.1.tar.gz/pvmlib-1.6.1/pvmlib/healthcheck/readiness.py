from fastapi import APIRouter, HTTPException
from pvmlib.settings import get_settings
from pvmlib.schemas.readiness_schema import responses_readiness
from pvmlib.mongo_worker.mongo_worker_repository import MongoWorkerRepository
from pvmlib.logger import LoggerSingleton

settings = get_settings()
readiness_router = APIRouter()
logger = LoggerSingleton().get_logger()

@readiness_router.get(
    "/healthcheck/readness", 
    tags=["Health Check"], 
    responses=responses_readiness, 
    summary="Status de los recursos"
)
async def readiness() -> dict:
    """ Comprueba que el servicio este operando """
    try:
        database_url = settings.MONGO_URI
        if not database_url:
            logger.error("URL_DB environment variable not found")
            raise Exception("URL_DB environment variable not found")
        # Aquí puedes agregar más lógica para comprobar la disponibilidad de otros recursos
        return {"status": "UP"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Readiness check failed")