from fastapi import APIRouter, Depends
from pvmlib.settings import get_settings 
from pvmlib.schemas.liveness_schema import (
    responses_liveness,
)

settings = get_settings()

liveness_router = APIRouter()


@liveness_router.get(
    "/healthcheck/liveness", 
    tags=["Health Check"], 
    responses=responses_liveness, 
    summary="Status del servicio"
)
def liveness() -> dict:
    """ Comprueba que el servicio este operando """
    return {"status": "UP"}
