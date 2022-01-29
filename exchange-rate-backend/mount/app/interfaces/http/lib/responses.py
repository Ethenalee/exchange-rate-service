"""Helper methods common to all api entry points"""
import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List

import pydantic
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse as StarletteJSONResponse

from app.commons.json import dumps
from app.commons.exceptions import AppError


@dataclass
class FieldError:
    code: str
    field: str
    message: str


class JSONResponse(StarletteJSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return dumps(content).encode("utf-8")


class EmptyResponse(JSONResponse):
    def __init__(self, status_code: int = 204, headers=None):
        super().__init__(None, status_code=status_code, headers=headers)


class SuccessResponse(JSONResponse):
    def __init__(self, data, meta: Dict = None, status_code: int = 200, headers=None):
        meta = meta if meta else {}
        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)
        elif isinstance(data, pydantic.BaseModel):
            data = data.dict()

        envelope = {"data": data, "meta": meta}

        super().__init__(envelope, status_code=status_code, headers=headers)


class ErrorResponse(JSONResponse):
    def __init__(
        self,
        code: str,
        message: str,
        field_errors: List[FieldError] = None,
        status_code: int = 500,
    ):
        content = {"code": code, "message": message}
        if field_errors:
            content["field_errors"] = list(
                map(dataclasses.asdict, field_errors))
        envelope = {"errors": [content]}

        super().__init__(envelope, status_code=status_code)

    @staticmethod
    def from_exception(error: AppError, status_code: int = 400):
        return ErrorResponse(error.code, error.message, status_code=status_code)


class ValidationErrorResponse(ErrorResponse):
    def __init__(self, field_errors: List[FieldError], status_code: int = 422):
        super().__init__(
            code="validation_error",
            message="One or more fields raised validation errors",
            field_errors=field_errors,
            status_code=status_code,
        )

    @staticmethod
    def from_exception(error: RequestValidationError):
        return ValidationErrorResponse(
            [
                FieldError(
                    code=err["type"],
                    field=".".join(err["loc"]),
                    message=err["msg"],
                )
                for err in error.errors()
            ]
        )


def success(data, status_code=200):  # pragma: no cover
    resp = {"status": "success", "data": data}

    return _response_from_dict(resp, status_code)


def failure(errors, status_code=400):  # pragma: no cover
    errors = errors if isinstance(errors, list) else [errors]
    resp = {"status": "error", "errors": errors}

    return _response_from_dict(resp, status_code)


def _response_from_dict(resp, status_code, **kwargs):
    return JSONResponse(
        resp, status_code=status_code, headers=kwargs.get("headers", None)
    )
