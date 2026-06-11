from fastapi import Request
from fastapi.responses import JSONResponse


# Custom exception class for controlled application errors
class MrFridgeException(Exception):
    def __init__(self, error_type: str, message: str, status_code: int = 400):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code


# 1. Handler for intentional errors we raise (MrFridgeException)
async def mrfridge_exception_handler(request: Request, exc: MrFridgeException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_type": exc.error_type,
            "message": exc.message,
        },
    )


# 2. Handler for unexpected system errors (Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # In a production project, add logging here (e.g. Sentry)
    return JSONResponse(
        status_code=500,
        content={
            "status": "fatal_error",
            "error_type": "InternalServerError",
            "message": "An unexpected error occurred on the server.",
            "details": str(exc),  # Visible during development for debugging
        },
    )
