"""
api_key_store.py — Merkezi OpenAI API key yöneticisi.
Key buradan okunur/yazılır; llm_service ve vision_service buraya başvurur.
"""
import os
import pathlib
from dotenv import load_dotenv

# .env dosyasının konumu (backend/ klasörü)
_ENV_PATH = pathlib.Path(__file__).parent.parent / ".env"


def _load_from_env():
    """Uygulama başlarken .env'den key'i oku."""
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    return os.getenv("OPENAI_API_KEY", "")


# Başlangıçta yükle
_current_key: str = _load_from_env()


def get_api_key() -> str:
    """Mevcut API key'i döndür."""
    return _current_key


def set_api_key(new_key: str) -> None:
    """
    Yeni API key'i ayarla:
    1. os.environ'u güncelle (anlık etki)
    2. backend/.env dosyasına yaz (kalıcı)
    3. llm_service ve vision_service client'larını sıfırla
    """
    global _current_key
    _current_key = new_key.strip()

    # os.environ güncelle
    os.environ["OPENAI_API_KEY"] = _current_key

    # .env dosyasına yaz (varsa güncelle, yoksa oluştur)
    _write_env_file(_current_key)

    # Servis client'larını sıfırla (lazy re-init için)
    _reset_clients()


def _write_env_file(key: str) -> None:
    """backend/.env dosyasını yazar/günceller."""
    env_path = _ENV_PATH
    lines = []

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # OPENAI_API_KEY satırını güncelle veya ekle
    key_line = f"OPENAI_API_KEY={key}\n"
    found = False
    for i, line in enumerate(lines):
        if line.startswith("OPENAI_API_KEY="):
            lines[i] = key_line
            found = True
            break
    if not found:
        lines.append(key_line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _reset_clients() -> None:
    """llm_service ve vision_service'deki cached client'ları sıfırla."""
    try:
        import services.llm_service as llm
        llm._client = None
        llm.API_KEY = _current_key
    except Exception:
        pass
    try:
        import services.vision_service as vis
        vis.API_KEY = _current_key
    except Exception:
        pass


def has_valid_key() -> bool:
    """Geçerli bir key var mı?"""
    k = _current_key
    return bool(k) and len(k) > 20 and not k.startswith("sk-test")
