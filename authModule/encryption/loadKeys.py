from pathlib import Path
from cryptography.hazmat.primitives import serialization
from functools import lru_cache
from config import PUBLIC_KEY_PATH
from env import EnvConfig

# Use paths from env.py (NOT app.py)
KEYS_DIR = Path(EnvConfig.KEYS_DIR)


@lru_cache(maxsize=1)
def load_server_public_key():
    with open(EnvConfig.PUBLIC_KEY_PATH, "rb") as f:
        return f.read()


@lru_cache(maxsize=32)
def load_private_key(key_id: str):
    private_path = KEYS_DIR / f"private_{key_id}.pem"
    if not private_path.exists():
        raise Exception("Invalid key_id")

    with open(private_path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )
