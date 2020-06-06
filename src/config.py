import collections
import json
import os
from functools import reduce
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_ROOT = PROJECT_ROOT / "data"
DOWNLOAD_DIR = DATA_ROOT / "download"
UPLOAD_DIR = DATA_ROOT / "upload"

env = os.environ
secret_key = env.get("secret_key")
user = env.get("user")
password = env.get("pass")


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(lambda d, k: d.get(k), items, root)


def set_by_path(root: dict, items, value):
    """Set a value in a nested object in root by item sequence."""
    for key in items[:-1]:
        root.setdefault(key, {})
        root = root[key]
    root[items[-1]] = value


def get_from_cache(*path):
    """Access a value from the global cache"""
    try:
        return get_by_path(global_path_cache_dict, path)
    except AttributeError:
        return None


def set_to_cache(*path, value=None):
    """Access a value from the global cache"""
    return set_by_path(global_path_cache_dict, path, value)


def save_cache():
    DATA_ROOT.joinpath("cache", "cache.json").write_text(json.dumps(global_path_cache_dict), encoding="UTF8")


def load_cache() -> dict:
    try:
        return json.loads(DATA_ROOT.joinpath("cache", "cache.json").read_text(encoding="UTF8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(
            b64_cache=dict(),
            session_cache=dict(),
        )


global_path_cache_dict = load_cache()
