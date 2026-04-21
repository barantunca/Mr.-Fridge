"""
routes_settings.py — Uygulama ayarları endpoint'leri
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.api_key_store import get_api_key, set_api_key, has_valid_key

router = APIRouter(prefix="/settings", tags=["settings"])


class ApiKeyRequest(BaseModel):
    api_key: str


class ApiKeyResponse(BaseModel):
    status: str          # "ok" | "error"
    has_key: bool
    masked_key: str      # "sk-...XXXX" formatında (güvenlik için maskelendi)
    message: str


def _mask_key(key: str) -> str:
    """Güvenlik için key'in sadece son 4 karakterini göster."""
    if not key or len(key) < 8:
        return "—"
    return f"sk-...{key[-4:]}"


@router.get("/api-key", response_model=ApiKeyResponse)
async def get_api_key_status():
    """Mevcut API key durumunu döndür (key değerini değil, sadece var mı yok mu)."""
    key = get_api_key()
    return ApiKeyResponse(
        status="ok",
        has_key=has_valid_key(),
        masked_key=_mask_key(key),
        message="API key mevcut." if has_valid_key() else "API key girilmemiş.",
    )


@router.post("/api-key", response_model=ApiKeyResponse)
async def update_api_key(body: ApiKeyRequest):
    """Yeni OpenAI API key'ini kaydet ve anlık olarak aktif et."""
    new_key = body.api_key.strip()

    if not new_key:
        raise HTTPException(status_code=400, detail="API key boş olamaz.")
    if len(new_key) < 20:
        raise HTTPException(status_code=400, detail="Geçersiz API key formatı.")

    set_api_key(new_key)

    return ApiKeyResponse(
        status="ok",
        has_key=True,
        masked_key=_mask_key(new_key),
        message="API key başarıyla kaydedildi!",
    )


@router.delete("/api-key", response_model=ApiKeyResponse)
async def delete_api_key():
    """Kayıtlı API key'i sil."""
    set_api_key("")
    return ApiKeyResponse(
        status="ok",
        has_key=False,
        masked_key="—",
        message="API key silindi.",
    )
