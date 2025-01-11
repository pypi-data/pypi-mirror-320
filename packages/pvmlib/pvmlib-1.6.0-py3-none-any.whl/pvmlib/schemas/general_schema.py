from pydantic import BaseModel, Field

class DataSchema(BaseModel):
    """
        Data Schema
    """
    status: str = Field(
        title="Status",
        description="Estatus de los servicios utilizados"
    )


class ErrorDataSchema(BaseModel):
    """
        Error Data Schema
    """
    user_message: str = Field(
        title="User Message",
        description="Mensaje de error para el usuario"
    )


class MetaSchema(BaseModel):
    """
        Meta Schema
    """
    time_elapsed: float = Field(
        default=1.0,
        title="Time elapsed",
        description="Tiempo que duró la operación"
    )
    timestamp: str = Field(
        default="2023-02-24T09:09:39.196026",
        title="Timestamp",
        description="Fecha en formato UTC"
    )
    transaction_id: str = Field(
        default="b284993c-323b-455a-87b9-ebf70b62bfa2",
        title="Transaction ID",
        description="Identificador único de la operación"
    )


class ErrorMetaSchema(BaseModel):
    """
        Error Meta Schema
    """
    details: list | dict | str | None = Field(
        title="Error Details",
        description="Datos adicionales del error",
        default=None
    )
    error_code: int = Field(
        title="Error Code",
        description="Identificador único del error"
    )
    info: str = Field(
        title="Info",
        description="URL donde se encuentra información más detallada del error"
    )
    timestamp: str = Field(
        default="2023-02-24T09:09:39.196026",
        title="Timestamp",
        description="Fecha en formato UTC"
    )
    transaction_id: str = Field(
        default="b284993c-323b-455a-87b9-ebf70b62bfa2",
        title="Transaction ID",
        description="Identificador único de la operación"
    )