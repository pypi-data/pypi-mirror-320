from pydantic import BaseModel
from typing import Any, Dict, Optional

class ErrorDataSchema(BaseModel):
    user_message: str

class ErrorMetaSchema(BaseModel):
    error_code: int
    info: str

class ErrorGeneralSchema(BaseModel):
    error: ErrorDataSchema
    trace: ErrorMetaSchema

type_content = "application/json"

error_general_schema = {
    "definitions": {
        "ErrorGeneralSchema": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "user_message": {"type": "string"}
                    }
                },
                "trace": {
                    "type": "object",
                    "properties": {
                        "error_code": {"type": "integer"},
                        "info": {"type": "string"}
                    }
                }
            }
        }
    }
}

error_response_general_405 = {
    "description": "Method Not Allowed",
    "content": {
        type_content: {
            "schema": error_general_schema["definitions"]["ErrorGeneralSchema"],
            "examples": {
                "MethodNotAllowed": {
                    "value": ErrorGeneralSchema(
                        error=ErrorDataSchema(user_message="Método no permitido."),
                        trace=ErrorMetaSchema(
                            error_code=405,
                            info="405"
                        )
                    ).model_dump()
                }
            }
        }
    }
}