"""
api_key_store.py — Centralized OpenAI API key manager.
The key is read/written here; llm_service and vision_service reference this module.
"""
import os
import pathlib
from dotenv import load_dotenv

# Location of the .env file (backend/ directory)
_ENV_PATH = pathlib.Path(__file__).parent.parent / ".env"


def _load_from_env():
    """Read the key from .env on application startup."""
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    return os.getenv("OPENAI_API_KEY", "")


# Load on startup
_current_key: str = _load_from_env()


def get_api_key() -> str:
    """Return the current API key."""
    return _current_key


def set_api_key(new_key: str) -> None:
    """
    Set a new API key:
    1. Update os.environ (immediate effect)
    2. Write to backend/.env (persistent)
    3. Reset llm_service and vision_service clients (lazy re-init)
    """
    global _current_key
    _current_key = new_key.strip()

    # Update os.environ
    os.environ["OPENAI_API_KEY"] = _current_key

    # Write to .env file (create if not exists, update if exists)
    _write_env_file(_current_key)

    # Reset service clients (for lazy re-initialization)
    _reset_clients()


def _write_env_file(key: str) -> None:
    """Writes/updates the backend/.env file."""
    env_path = _ENV_PATH
    lines = []

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Update or append the OPENAI_API_KEY line
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
    """Reset cached clients in llm_service and vision_service."""
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
    """Returns True if a valid key is configured."""
    k = _current_key
    return bool(k) and len(k) > 20 and not k.startswith("sk-test")
