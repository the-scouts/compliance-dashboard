import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_ROOT = PROJECT_ROOT / "data"
DOWNLOAD_DIR = DATA_ROOT / "download"
UPLOAD_DIR = DATA_ROOT / "upload"

secret_key = os.environ.get("secret_key")  # Flask Secret Key
is_production = False if os.environ.get("dev_env") else True

user = os.environ.get("user")
password = os.environ.get("pass")

redis_host = os.environ.get("REDIS_HOST")
redis_key = os.environ.get("REDIS_KEY")