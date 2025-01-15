from fastapi import APIRouter
from pvmlib.response_config.healthcheck_reponse import responses_liveness, LivenessResponse
from pvmlib.logs import LoggerSingleton

liveness_router = APIRouter()
logger = LoggerSingleton().get_logger()

@liveness_router.get(
    "/healthcheck/liveness", 
    tags=["Health Check"], 
    responses=responses_liveness, 
    summary="Status del servicio",
    response_model=LivenessResponse
)
async def liveness() -> LivenessResponse:
    """ Comprueba que el servicio este operando """
    return LivenessResponse(
        status="UP",
        code=200,
        dependencies={}
    )