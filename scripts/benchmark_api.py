from __future__ import annotations

import argparse
import logging
import math
import statistics
import time
from pathlib import Path

from fastapi.testclient import TestClient

from phishing_detector.api import create_app
from phishing_detector.config import Settings


def percentile(values: list[float], percent: float) -> float:
    return sorted(values)[max(0, math.ceil(len(values) * percent) - 1)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure lexical-only prediction latency in-process.")
    parser.add_argument("--model", type=Path, default=Path("models/phishing_model.joblib"))
    parser.add_argument("--runs", type=int, default=100)
    args = parser.parse_args()
    logging.getLogger("phishing_detector.api").disabled = True
    logging.getLogger("httpx").disabled = True
    app = create_app(Settings(model_path=args.model))
    samples: list[float] = []
    with TestClient(app) as client:
        for _ in range(args.runs):
            start = time.perf_counter()
            response = client.post("/predict", json={"url": "https://example.com/"})
            response.raise_for_status()
            samples.append((time.perf_counter() - start) * 1_000)
    print(f"runs={args.runs} p50_ms={statistics.median(samples):.3f} p95_ms={percentile(samples, 0.95):.3f} max_ms={max(samples):.3f}")


if __name__ == "__main__":
    main()
