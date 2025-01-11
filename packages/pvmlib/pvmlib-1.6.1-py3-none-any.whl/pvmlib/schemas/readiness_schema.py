from pydantic import BaseModel, Field
from .general_schema import (
    DataSchema, 
    MetaSchema
)
from .errors_schema import (
    error_response_general_405,
)


class ReadinessSchema(BaseModel):
    """
        Readiness Schema
    """
    data: DataSchema = Field(
        default=DataSchema(status="Mongo are up"),
        title="DataSchema"
    )
    meta: MetaSchema = Field(...)


responses_readiness = {
    200: {"model": ReadinessSchema},
    405: error_response_general_405
    }