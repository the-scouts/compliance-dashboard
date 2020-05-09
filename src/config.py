import os
from pathlib import Path

PROJECT_ROOT = Path("./").resolve().absolute()
DOWNLOAD_DIR = PROJECT_ROOT / "download"

env = os.environ
secret_key = env.get("secret_key")
user = env.get("user")
password = env.get("pass")
