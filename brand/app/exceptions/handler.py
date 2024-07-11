from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any


def format_validation_error(error):
    loc = error.get("loc", [])
    msg = error.get("msg", "")

    if loc and isinstance(loc, tuple):
        field_name = loc[-1]  # Get the last item in the location list
        return f"{field_name} {msg}"
    return msg


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Extract error messages
    errors = exc.errors()

    # custom_error_messages = [error["msg"] for error in errors]
    custom_error_messages = [format_validation_error(error) for error in errors]

    return JSONResponse(
        status_code=400,
        content={"errors": custom_error_messages},
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"errors": [exc.detail]},
    )
