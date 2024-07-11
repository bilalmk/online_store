from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import traceback

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "code": 422,
                    "detail": exc.errors()
                },
            )
        except StarletteHTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "code": exc.status_code,
                    "detail": exc.detail
                },
            )
        except Exception as exc:
            # Log the traceback for debugging purposes
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "detail": "Internal Server Error"
                },
            )

# Initialize the FastAPI app
app = FastAPI()

# Add the middleware to the app
app.add_middleware(ExceptionHandlingMiddleware)
