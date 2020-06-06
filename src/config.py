import os
from pathlib import Path
from functools import reduce
import json

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_ROOT = PROJECT_ROOT / "data"
DOWNLOAD_DIR = DATA_ROOT / "download"
UPLOAD_DIR = DATA_ROOT / "upload"

env = os.environ
secret_key = env.get("secret_key")
user = env.get("user")
password = env.get("pass")
