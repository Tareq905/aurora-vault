import os
from platformdirs import user_cache_dir

CACHE_DIR = user_cache_dir("aurora-vault")
DB_PATH = os.path.join(CACHE_DIR, "vault_index.db")

def ensure_dirs():
    os.makedirs(CACHE_DIR, exist_ok=True)