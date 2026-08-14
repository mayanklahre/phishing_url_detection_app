import pytest

from phishing_detector.security import UnsafeUrl, normalize_url, validate_public_url


def test_normalize_url_adds_https() -> None:
    assert normalize_url("example.com/login").geturl() == "https://example.com/login"


@pytest.mark.parametrize("url", ["file:///etc/passwd", "https://user:pass@example.com", "https://example.com:8443/", "http://127.0.0.1/"])
def test_unsafe_targets_are_rejected(url: str) -> None:
    with pytest.raises(UnsafeUrl):
        validate_public_url(url)
