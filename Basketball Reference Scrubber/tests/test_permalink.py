from scrubber.config import Settings
from scrubber.share.permalink import PermalinkStore, build_permalink, decode_state, encode_state


def test_stateless_roundtrip():
    state = {"intent": "compare", "players": ["LeBron James", "Kevin Durant"], "season": "2023-24"}
    token = encode_state(state)
    assert decode_state(token) == state


def test_build_permalink_shape():
    url = build_permalink({"a": 1}, base_url="https://example.com")
    assert url.startswith("https://example.com/p/")


def test_permalink_store_create_and_resolve(tmp_path):
    settings = Settings(cache_dir=tmp_path)
    store = PermalinkStore(settings=settings)
    short_id = store.create({"foo": "bar"})
    assert store.resolve(short_id) == {"foo": "bar"}


def test_permalink_store_missing_id_returns_none(tmp_path):
    settings = Settings(cache_dir=tmp_path)
    store = PermalinkStore(settings=settings)
    assert store.resolve("doesnotexist") is None
