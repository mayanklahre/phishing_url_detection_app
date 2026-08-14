from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import SplitResult, urlsplit, urlunsplit


class UnsafeUrl(ValueError):
    """Raised when a URL is malformed or unsafe to contact from the service."""


@dataclass(frozen=True)
class SafeUrl:
    normalized: str
    host: str
    port: int
    addresses: tuple[str, ...]


def normalize_url(value: str, *, network_safe: bool = False) -> SplitResult:
    value = value.strip()
    if not value:
        raise UnsafeUrl("url is required")
    parsed = urlsplit(value if "://" in value else f"https://{value}")
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrl("only http and https URLs are allowed")
    if not parsed.hostname:
        raise UnsafeUrl("URL must contain a hostname")
    if network_safe:
        if parsed.username or parsed.password:
            raise UnsafeUrl("URLs with embedded credentials are not allowed")
        try:
            port = parsed.port
        except ValueError as error:
            raise UnsafeUrl("invalid port") from error
        if port not in {None, 80, 443}:
            raise UnsafeUrl("only ports 80 and 443 are allowed")
    return parsed


def _is_public(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_public_url(value: str) -> SafeUrl:
    """Normalize and resolve a URL, rejecting private/reserved network targets.

    Call this immediately before every outbound operation. Redirects are disabled in
    the extractor, so a redirect cannot bypass this validation.
    """

    parsed = normalize_url(value, network_safe=True)
    host = (parsed.hostname or "").rstrip(".").lower()
    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as error:
        raise UnsafeUrl("hostname could not be resolved") from error
    addresses = tuple(sorted({item[4][0] for item in infos}))
    if not addresses or any(not _is_public(address) for address in addresses):
        raise UnsafeUrl("private, reserved, or mixed-address targets are not allowed")
    netloc = host if parsed.port is None else f"{host}:{parsed.port}"
    normalized = urlunsplit((parsed.scheme, netloc, parsed.path or "/", parsed.query, ""))
    return SafeUrl(normalized, host, parsed.port or (443 if parsed.scheme == "https" else 80), addresses)
