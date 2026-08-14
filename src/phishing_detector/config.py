from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime settings with safe defaults for outbound feature collection."""

    model_path: Path = Path(os.getenv("MODEL_PATH", "models/phishing_model.joblib"))
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "2.0"))
    whois_timeout_seconds: float = float(os.getenv("WHOIS_TIMEOUT_SECONDS", "2.0"))
    retries: int = int(os.getenv("FEATURE_RETRIES", "1"))
    cache_ttl_seconds: int = int(os.getenv("FEATURE_CACHE_TTL_SECONDS", "900"))
    max_html_bytes: int = int(os.getenv("MAX_HTML_BYTES", "65536"))
    user_agent: str = os.getenv("FEATURE_USER_AGENT", "PhishingDetector/1.0 (+security-research)")


settings = Settings()
