from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx

PHISHING_DATABASE_FEED = "https://raw.githubusercontent.com/Phishing-Database/Phishing.Database/master/phishing-links-ACTIVE.txt"
TRANCO_ZIP = "https://tranco-list.eu/top-1m.csv.zip"


def _valid_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and "@" not in value
    except ValueError:
        return False


def _download(url: str) -> bytes:
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def _phishing_database_urls(content: bytes, limit: int) -> list[str]:
    urls: list[str] = []
    for line in content.decode("utf-8", errors="replace").splitlines():
        url = line.strip()
        if _valid_url(url):
            urls.append(url)
        if len(urls) >= limit:
            break
    return urls


def _tranco_urls(content: bytes, limit: int) -> list[str]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".csv"))
        text = archive.read(name).decode("utf-8", errors="replace")
    urls: list[str] = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2:
            continue
        domain = row[1].strip().lower()
        if domain and "." in domain:
            urls.append(f"https://{domain}/")
        if len(urls) >= limit:
            break
    return urls


def build_dataset(output: Path, manifest: Path, malicious_count: int = 25_000, benign_count: int = 25_000) -> dict[str, object]:
    """Build a labelled CSV with URLs only; no URL is contacted during this step."""

    phishing_blob = _download(PHISHING_DATABASE_FEED)
    tranco_blob = _download(TRANCO_ZIP)
    malicious = _phishing_database_urls(phishing_blob, malicious_count)
    benign = _tranco_urls(tranco_blob, benign_count)
    if len(malicious) < malicious_count:
        raise RuntimeError(f"Phishing.Database returned only {len(malicious)} valid URLs; requested {malicious_count}")
    if len(benign) < benign_count:
        raise RuntimeError(f"Tranco returned only {len(benign)} valid domains; requested {benign_count}")
    labelled: dict[str, int] = {url: 1 for url in malicious}
    for url in benign:
        labelled.setdefault(url, 0)
    rows = sorted(labelled.items())
    if len(rows) < malicious_count + benign_count:
        raise RuntimeError("source overlap prevented the requested dataset size")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["url", "label"])
        writer.writerows(rows)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    metadata = {
        "dataset_version": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(rows),
        "class_counts": {"phishing": sum(label for _, label in rows), "legitimate": sum(1 - label for _, label in rows)},
        "sha256": digest,
        "sources": [{"name": "Phishing.Database active link feed", "url": PHISHING_DATABASE_FEED, "sha256": hashlib.sha256(phishing_blob).hexdigest()}, {"name": "Tranco Top 1M", "url": TRANCO_ZIP, "sha256": hashlib.sha256(tranco_blob).hexdigest()}],
        "notes": "Rows are URL labels only. Training extracts lexical features offline; live network enrichment is opt-in at API time.",
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reproducible labelled URL dataset from public feeds.")
    parser.add_argument("--output", type=Path, default=Path("data/urls.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("data/dataset_manifest.json"))
    parser.add_argument("--malicious-count", type=int, default=25_000)
    parser.add_argument("--benign-count", type=int, default=25_000)
    args = parser.parse_args()
    print(json.dumps(build_dataset(args.output, args.manifest, args.malicious_count, args.benign_count), indent=2))


if __name__ == "__main__":
    main()
