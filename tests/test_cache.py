from phishing_detector.cache import TTLCache


def test_cache_returns_a_copy() -> None:
    cache: TTLCache[dict[str, bool]] = TTLCache(ttl_seconds=60)
    cache.set("url", {"cached": False})
    cached = cache.get("url")
    assert cached == {"cached": False}
    assert cached is not None
    cached["cached"] = True
    assert cache.get("url") == {"cached": False}
