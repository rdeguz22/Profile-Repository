from scrubber.cache import DiskCache


def test_set_and_get(tmp_path):
    cache = DiskCache(tmp_path / "c.sqlite3")
    key = cache.make_key("ns", {"a": 1})
    assert cache.get(key, ttl_seconds=60) is None

    cache.set(key, {"hello": "world"})
    assert cache.get(key, ttl_seconds=60) == {"hello": "world"}


def test_ttl_expiry(tmp_path):
    cache = DiskCache(tmp_path / "c.sqlite3")
    key = cache.make_key("ns", {"a": 1})
    cache.set(key, {"x": 1})
    assert cache.get(key, ttl_seconds=-1) is None


def test_clear(tmp_path):
    cache = DiskCache(tmp_path / "c.sqlite3")
    key = cache.make_key("ns", {"a": 1})
    cache.set(key, {"x": 1})
    cache.clear()
    assert cache.get(key, ttl_seconds=60) is None


def test_key_stable_for_same_params(tmp_path):
    cache = DiskCache(tmp_path / "c.sqlite3")
    key1 = cache.make_key("ns", {"a": 1, "b": 2})
    key2 = cache.make_key("ns", {"b": 2, "a": 1})
    assert key1 == key2
