from pydantic import BaseModel
from typing import Any, Dict

class ResponseMetaSchema(BaseModel):
    id_transaction: str
    status: str
    time_elapsed: float

class ResponseGeneralSchema(BaseModel):
    code: int = 0
    type: int = 0
    message: str = "SUCCESS"
    data: Dict[str, Any]
    meta: ResponseMetaSchema

type_content = "application/json"

success_general_schema = {
    "definitions": {
        "ResponseGeneralSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "type": {"type": "integer"},
                "message": {"type": "string"},
                "data": {"type": "object"},
                "meta": {
                    "type": "object",
                    "properties": {
                        "id_transaction": {"type": "string"},
                        "status": {"type": "string"},
                        "time_elapsed": {"type": "number"}
                    }
                }
            }
        }
    }
}

success_response_example = {
    "description": "Successful Response",
    "content": {
        type_content: {
            "schema": success_general_schema["definitions"]["ResponseGeneralSchema"],
            "examples": {
                "SuccessExample": {
                    "value": ResponseGeneralSchema(
                        code=0,
                        type=0,
                        message="Success",
                        data={"dns": "https://pvm-stg.coppel.io/puntodeventa/api/v1/"},
                        meta=ResponseMetaSchema(
                            id_transaction="bdae4708-72fd-49a8-8f73-646605101072",
                            status="SUCCESS",
                            time_elapsed=2.7139980792999268
                        )
                    ).model_dump()
                }
            }
        }
    }
}