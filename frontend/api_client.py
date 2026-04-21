"""
api_client.py — Mr. Fridge backend ile tüm HTTP iletişimi burada yapılır.
"""
import requests

from kivy.utils import platform

# Android'de test ediliyorsa cihazın ağ IP'si veya emulator IP'si kullanılır
if platform == 'android':
    BASE_URL = "http://10.0.2.2:8000"  # Fiziksel cihaz için burayı Wi-Fi IP'nizle (Örn: 192.168.x.x) değiştirin
else:
    BASE_URL = "http://127.0.0.1:8000"
FRIDGE_ID = 1  # Şimdilik sabit


def _handle_error(e: Exception) -> dict:
    return {"error": str(e)}


# ── CAMERA ────────────────────────────────────────────────────────────────────

def scan_item(base64_image: str) -> dict:
    """POST /camera/scan → {"name": str, "category": str}"""
    try:
        resp = requests.post(
            f"{BASE_URL}/camera/scan",
            json={"base64_image": base64_image},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return _handle_error(e)


# ── INVENTORY ─────────────────────────────────────────────────────────────────

def get_inventory_items(fridge_id: int = FRIDGE_ID) -> list:
    """GET /inventory/{id}/items → [{"id": int, "name": str, "category": str}]"""
    try:
        resp = requests.get(f"{BASE_URL}/inventory/{fridge_id}/items", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def add_item(name: str, category: str, fridge_id: int = FRIDGE_ID) -> dict:
    """POST /inventory/add"""
    try:
        resp = requests.post(
            f"{BASE_URL}/inventory/add",
            json={"fridge_id": fridge_id, "name": name, "category": category},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return _handle_error(e)


def delete_item(item_id: int) -> dict:
    """DELETE /inventory/delete/{item_id}"""
    try:
        resp = requests.delete(
            f"{BASE_URL}/inventory/delete/{item_id}", timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return _handle_error(e)


def get_categorized_inventory(fridge_id: int = FRIDGE_ID) -> dict:
    """GET /inventory/{id}/categorized → {"Sebze": ["Domates", ...], ...}"""
    try:
        resp = requests.get(
            f"{BASE_URL}/inventory/{fridge_id}/categorized", timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


# ── RECIPE ────────────────────────────────────────────────────────────────────

def generate_recipe_stream(ingredients: list):
    """POST /recipe/generate — streaming. Generator: chunk'ları yield eder."""
    try:
        with requests.post(
            f"{BASE_URL}/recipe/generate",
            json={"ingredients": ingredients},
            stream=True,
            timeout=60,
        ) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=None):
                if chunk:
                    yield chunk.decode("utf-8")
    except Exception as e:
        yield f"\n[Hata: {e}]"


# ── SETTINGS ──────────────────────────────────────────────────────────────────

def get_api_key_status() -> dict:
    """GET /settings/api-key → {has_key, masked_key, message}"""
    try:
        resp = requests.get(f"{BASE_URL}/settings/api-key", timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e), "has_key": False, "masked_key": "—", "message": ""}


def save_api_key(api_key: str) -> dict:
    """POST /settings/api-key — yeni key'i backend'e kaydet."""
    try:
        resp = requests.post(
            f"{BASE_URL}/settings/api-key",
            json={"api_key": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return _handle_error(e)


def delete_api_key() -> dict:
    """DELETE /settings/api-key — kayıtlı key'i sil."""
    try:
        resp = requests.delete(f"{BASE_URL}/settings/api-key", timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return _handle_error(e)
