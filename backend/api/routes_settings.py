"""
routes_settings.py — Application settings endpoints
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
    masked_key: str      # "sk-...XXXX" format (masked for security)
    message: str


def _mask_key(key: str) -> str:
    """Show only the last 4 characters of the key for security."""
    if not key or len(key) < 8:
        return "—"
    return f"sk-...{key[-4:]}"


@router.get("/api-key", response_model=ApiKeyResponse)
async def get_api_key_status():
    """Returns the current API key status (existence only, not the value itself)."""
    key = get_api_key()
    return ApiKeyResponse(
        status="ok",
        has_key=has_valid_key(),
        masked_key=_mask_key(key),
        message="API key is configured." if has_valid_key() else "No API key has been set.",
    )


@router.post("/api-key", response_model=ApiKeyResponse)
async def update_api_key(body: ApiKeyRequest):
    """Saves a new OpenAI API key and activates it immediately."""
    new_key = body.api_key.strip()

    if not new_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
    if len(new_key) < 20:
        raise HTTPException(status_code=400, detail="Invalid API key format.")

    set_api_key(new_key)

    return ApiKeyResponse(
        status="ok",
        has_key=True,
        masked_key=_mask_key(new_key),
        message="API key saved successfully!",
    )


@router.delete("/api-key", response_model=ApiKeyResponse)
async def delete_api_key():
    """Removes the stored API key."""
    set_api_key("")
    return ApiKeyResponse(
        status="ok",
        has_key=False,
        masked_key="—",
        message="API key has been deleted.",
    )
