from fastapi import Request
from fastapi.responses import JSONResponse


# Uygulamaya özel fırlatacağımız kontrollü hata sınıfı
class MrFridgeException(Exception):
    def __init__(self, error_type: str, message: str, status_code: int = 400):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code


# 1. Bizim bilerek fırlattığımız hataları (MrFridgeException) yakalayacak fonksiyon
async def mrfridge_exception_handler(request: Request, exc: MrFridgeException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_type": exc.error_type,
            "message": exc.message,
        },
    )


# 2. Gözden kaçan, sistemin fırlattığı genel hataları (Exception) yakalayacak fonksiyon
async def global_exception_handler(request: Request, exc: Exception):
    # Gerçek bir projede buraya loglama (Sentry vb.) eklenir
    return JSONResponse(
        status_code=500,
        content={
            "status": "fatal_error",
            "error_type": "InternalServerError",
            "message": "Sunucu tarafında beklenmeyen bir hata oluştu.",
            "details": str(exc),  # Geliştirme aşamasında hatayı görmek için
        },
    )
