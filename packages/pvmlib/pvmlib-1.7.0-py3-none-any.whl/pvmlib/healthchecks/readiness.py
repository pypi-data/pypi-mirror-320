import os
from fastapi import APIRouter, HTTPException
from pvmlib.response_config.healthcheck_reponse import responses_readiness, ReadinessResponse
from pvmlib.utils.dependecy_check import DependencyChecker, check_mongo, check_external_service
from pvmlib.database import DatabaseManager
from pvmlib.logs import LoggerSingleton

readiness_router = APIRouter()
logger = LoggerSingleton().get_logger()
database_manager = DatabaseManager()

# Obtiene las dependencias de los servicios con el endpoint del healthcheck // liveness o readiness
dependency_services = os.getenv("SERVICES_DEPENDENCY_HEALTHCHEK", "").split(",") 

@readiness_router.get(
    "/healthcheck/readness", 
    tags=["Health Check"], 
    responses=responses_readiness, 
    summary="Status de los recursos",
    response_model=ReadinessResponse
)
async def readiness() -> ReadinessResponse:
    """ Comprueba que el servicio este operando """
    dependencies = []

    # Verificar si hay servicios externos configurados
    if dependency_services and any(dependency_services):
        dependencies.extend([lambda url=url: check_external_service(url) for url in dependency_services if url])

    # Verificar si MongoDB está instanciada
    if database_manager.mongo_client:
        dependencies.append(lambda: check_mongo(database_manager))

    # Si no hay dependencias, devolver estado ready con dependencias vacías
    if not dependencies:
        logger.info("No dependencies to check. Returning ready status.")
        return ReadinessResponse(
            status="ready",
            code=200,
            dependencies={}
        )

    # Verificar las dependencias
    checker = DependencyChecker(dependencies=dependencies)
    dependencies_status = await checker.check_dependencies()

    logger.info(f"Dependencies status: {dependencies_status}")

    return ReadinessResponse(
        status="ready" if all(status == "UP" for status in dependencies_status.values()) else "not ready",
        code=200 if all(status == "UP" for status in dependencies_status.values()) else 500,
        dependencies=dependencies_status
    )