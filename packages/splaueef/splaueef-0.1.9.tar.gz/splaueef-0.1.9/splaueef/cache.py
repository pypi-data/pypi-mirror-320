import json

class LocalCache:
    def __init__(self, filename="cache.json"):
        self.filename = filename
        self._cache = self._load_cache()

    def _load_cache(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=4)

    def set(self, key, value):
        self._cache[key] = value
        self.save()

    def get(self, key):
        return self._cache.get(key)
