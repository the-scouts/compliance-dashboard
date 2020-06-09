import datetime
import json

import dash
import flask_caching
import redis

import src.config as config


class CacheInterface:
    cache_path = config.DATA_ROOT / "cache" / "cache.json"

    def __init__(self, app: dash.Dash):
        app.server.logger.info(f"REDIS: {config.redis_host} {config.redis_key}")

        self.cache: flask_caching.Cache = flask_caching.Cache(app.server, config=dict(
            CACHE_TYPE="redis",
            CACHE_REDIS_HOST=config.redis_host,
            CACHE_REDIS_PASSWORD="OFwueYfOjelJRYaFCbPZ0L4E6rlPzvLsGmyjLuIvVxU=",
            CACHE_REDIS_PORT=6380,
            CACHE_REDIS_DB=0,
            CACHE_OPTIONS={"ssl": True}
        ))
        self.r: redis.Redis = self.cache.cache._read_clients  # NoQA
        self.key_prefix = self.cache.cache.key_prefix
        self.environment = "prod" if config.is_production else "dev"
        self.app = app

    def _serialize_path(self, *path) -> str:
        return "/".join([self.environment, *path])

    @staticmethod
    def _set_by_path(root: dict, items, value):
        """Set a value in a nested object in root by item sequence."""
        for key in items[:-1]:
            root.setdefault(key, {})
            root = root[key]
        root[items[-1]] = value

    @staticmethod
    def _keys_to_strings(keys: list, key_prefix: str = "") -> list:
        return [key.decode("UTF8")[len(key_prefix):] for key in keys]  # TODO key.removeprefix(root) when py3.9 is released (Oct 20)

    def get_keys_from_partial(self, *path) -> list:
        """Return a list of keys from the global cache"""
        return self.r.keys(f"{self.key_prefix}{self._serialize_path(*path)}*")

    def get_dict_from_partial(self, *path):
        keys = self.get_keys_from_partial(*path)
        root = self._serialize_path(*path) + "/"
        stringified_keys = self._keys_to_strings(keys, self.key_prefix)
        results = {key[len(root):]: self.cache.get(key) for key in stringified_keys}  # TODO key.removeprefix(root) when py3.9 is released (Oct 20)
        tree = self._build_tree(results)
        return tree

    def get_from_cache(self, *path):
        """Access a value from the global cache"""
        return self.cache.get(self._serialize_path(*path))

    def set_to_cache(self, *path, value=None):
        """Access a value from the global cache"""
        return self.cache.set(self._serialize_path(*path), value)

    def build_tree(self):
        keys = self.r.keys()
        vals = self.cache.get_many(keys)
        pairs = dict(zip(keys, vals))
        tree = self._build_tree(pairs)
        return tree

    def _build_tree(self, pairs: dict) -> dict:
        """Builds nested directory tree from key-val dict with path-like keys"""
        tree = {}
        for key, val in pairs.items():
            self._set_by_path(tree, key.split("/"), val)
        return tree

    def get_key_timestamp(self, key: str) -> datetime.datetime:
        try:
            last_accessed = datetime.datetime.utcnow().timestamp() - self.r.object("idletime", key)
        except TypeError:
            return datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)  # If key doesn't exist
        return datetime.datetime.fromtimestamp(int(last_accessed), tz=datetime.timezone.utc)

    def save_to_disk(self):
        # Ensure state is not changed whilst getting data
        with self.r.lock("saving", timeout=5, blocking_timeout=2.5):
            keys = self.r.keys()
            vals = self.cache.get_many(*self._keys_to_strings(keys, self.key_prefix))
            timestamps = []
            for key in keys:
                timestamps.append(self.get_key_timestamp(key).isoformat())

        stringified_keys = self._keys_to_strings(keys, self.key_prefix)
        vals_with_timestamps = [*zip(vals, timestamps)]
        pairs = dict(zip(stringified_keys, vals_with_timestamps))
        json_pairs = json.dumps(pairs)
        self.cache_path.write_text(json_pairs, encoding="UTF8")

    def load_from_disk(self):
        try:
            loaded_json = json.loads(self.cache_path.read_text(encoding="UTF8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        self.app.server.logger.info(f"REDIS KEYS: {self.r.keys()}")

        parsed_json = {k: tuple(v) for k, v in loaded_json.items()}
        with self.r.lock("saving", timeout=5, blocking_timeout=2.5):
            for key, tpl in parsed_json.items():
                timestamp = tpl[1]
                if self.get_key_timestamp(key) < datetime.datetime.fromisoformat(timestamp):
                    value = tpl[0]
                    self.app.server.logger.info(f"replacing key {key} with value {value}")
                    self.cache.set(key, value)