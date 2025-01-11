from pydantic import BaseModel, Field
from .errors_schema import (
    error_response_general_405
)


class LivenessSchema(BaseModel):
    """
        Liveness Schema
    """
    status: str = Field(
        default="success",
        title="Status",
        description="Estatus del servicio"
    )


responses_liveness = {
    200: {"model": LivenessSchema},
    405: error_response_general_405
}