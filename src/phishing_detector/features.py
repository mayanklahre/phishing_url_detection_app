from __future__ import annotations

import concurrent.futures
import math
import re
import socket
import ssl
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit

import httpx
import whois
from bs4 import BeautifulSoup

from .cache import TTLCache
from .config import Settings, settings
from .security import SafeUrl, UnsafeUrl, normalize_url, validate_public_url

SUSPICIOUS_TOKENS = frozenset({"account", "auth", "bank", "confirm", "login", "password", "secure", "signin", "update", "verify", "wallet"})
LEXICAL_FEATURES = [
    "url_length", "host_length", "path_length", "digit_ratio", "dot_count", "hyphen_count",
    "subdomain_count", "query_parameter_count", "suspicious_token_count", "has_ip_host",
    "has_at_symbol", "uses_https", "url_entropy",
]
# These exclude scheme and path-shape fields that are easily distorted when
# combining a phishing-feed URL source with top-domain URLs. They are still
# returned by the API for interpretation, but are not used by the baseline
# model until a source-balanced crawl is available.
MODEL_FEATURES = [
    "host_length", "digit_ratio", "dot_count", "hyphen_count", "subdomain_count",
    "suspicious_token_count", "has_ip_host", "has_at_symbol", "url_entropy",
]


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    probabilities = [value.count(char) / len(value) for char in set(value)]
    return -sum(probability * math.log2(probability) for probability in probabilities)


def _is_ip_host(host: str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET, host)
        return True
    except OSError:
        try:
            socket.inet_pton(socket.AF_INET6, host)
            return True
        except OSError:
            return False


def lexical_features(url: str) -> dict[str, float]:
    parsed = normalize_url(url)
    host = (parsed.hostname or "").lower()
    full = url.lower()
    alpha_numeric = [char for char in full if char.isalnum()]
    return {
        "url_length": float(len(full)),
        "host_length": float(len(host)),
        "path_length": float(len(parsed.path)),
        "digit_ratio": float(sum(char.isdigit() for char in alpha_numeric) / max(1, len(alpha_numeric))),
        "dot_count": float(host.count(".")),
        "hyphen_count": float(host.count("-")),
        "subdomain_count": float(max(0, len([part for part in host.split(".") if part]) - 2)),
        "query_parameter_count": float(len(parse_qs(parsed.query, keep_blank_values=True))),
        "suspicious_token_count": float(sum(token in full for token in SUSPICIOUS_TOKENS)),
        "has_ip_host": float(_is_ip_host(host)),
        "has_at_symbol": float("@" in full),
        "uses_https": float(parsed.scheme == "https"),
        "url_entropy": _entropy(full),
    }


@dataclass
class LiveFeatureResult:
    values: dict[str, float | str | bool | None] = field(default_factory=dict)
    statuses: dict[str, str] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    cached: bool = False


class LiveFeatureExtractor:
    """Bounded, cached external enrichment. No redirect is ever followed."""

    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.cache: TTLCache[LiveFeatureResult] = TTLCache(config.cache_ttl_seconds)
        self._whois_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="whois")

    def extract(self, url: str) -> LiveFeatureResult:
        target = validate_public_url(url)
        cached = self.cache.get(target.normalized)
        if cached is not None:
            cached.cached = True
            return cached
        result = LiveFeatureResult()
        for name, extractor in (("dns", self._dns), ("tls", self._tls), ("http_html", self._http_html), ("whois", self._whois)):
            self._run_bounded(name, extractor, target, result)
        self.cache.set(target.normalized, result)
        return result

    def _run_bounded(self, name: str, extractor, target: SafeUrl, result: LiveFeatureResult) -> None:
        for attempt in range(self.config.retries + 1):
            try:
                values = extractor(target)
                result.values.update(values)
                result.statuses[name] = "ok"
                return
            except Exception as error:  # external services are expected to be unreliable
                if attempt == self.config.retries:
                    result.statuses[name] = "unavailable"
                    result.errors[name] = type(error).__name__
                else:
                    time.sleep(min(0.1 * (2**attempt), 0.25))

    def _dns(self, target: SafeUrl) -> dict[str, float | str | bool | None]:
        return {"dns_resolved": True, "dns_address_count": float(len(target.addresses)), "dns_addresses": ",".join(target.addresses)}

    def _tls(self, target: SafeUrl) -> dict[str, float | str | bool | None]:
        if urlsplit(target.normalized).scheme != "https":
            return {"tls_present": False, "tls_days_remaining": None}
        context = ssl.create_default_context()
        with socket.create_connection((target.addresses[0], 443), timeout=self.config.request_timeout_seconds) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=target.host) as tls_socket:
                certificate = tls_socket.getpeercert()
        expires = datetime.strptime(certificate["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        return {"tls_present": True, "tls_days_remaining": float((expires - datetime.now(timezone.utc)).days), "tls_issuer": str(certificate.get("issuer", ""))}

    def _http_html(self, target: SafeUrl) -> dict[str, float | str | bool | None]:
        # Revalidate before each network operation; redirects remain disabled.
        validate_public_url(target.normalized)
        headers = {"User-Agent": self.config.user_agent, "Accept": "text/html,application/xhtml+xml"}
        with httpx.Client(timeout=self.config.request_timeout_seconds, follow_redirects=False, headers=headers) as client:
            with client.stream("GET", target.normalized) as response:
                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    chunks.append(chunk)
                    total += len(chunk)
                    if total >= self.config.max_html_bytes:
                        break
                body = b"".join(chunks)[: self.config.max_html_bytes]
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            return {"http_status": float(response.status_code), "html_observed": False, "html_form_count": None, "html_external_form_action": None}
        soup = BeautifulSoup(body, "html.parser")
        forms = soup.find_all("form")
        external_actions = sum(1 for form in forms if str(form.get("action", "")).startswith(("http://", "https://")))
        return {"http_status": float(response.status_code), "html_observed": True, "html_form_count": float(len(forms)), "html_external_form_action": bool(external_actions), "html_script_count": float(len(soup.find_all("script")))}

    def _whois(self, target: SafeUrl) -> dict[str, float | str | bool | None]:
        future = self._whois_executor.submit(whois.whois, target.host)
        record = future.result(timeout=self.config.whois_timeout_seconds)
        creation_date = getattr(record, "creation_date", None)
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else None
        if isinstance(creation_date, datetime):
            age = (datetime.now(timezone.utc).replace(tzinfo=None) - creation_date.replace(tzinfo=None)).days
        else:
            age = None
        return {"whois_available": bool(record), "whois_domain_age_days": float(age) if age is not None else None}
