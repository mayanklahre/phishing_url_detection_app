# Phishing URL Detection API

A reproducible phishing URL classifier with a FastAPI service, lexical ML scoring, and opt-in live URL enrichment. It is designed to make its limits observable: the classifier is fast because it uses local lexical features, while slow or unavailable network features are returned separately with explicit status information.

## What is implemented

- A reproducible 50,000-row URL-label data build from Phishing.Database (phishing) and Tranco (legitimate), with source and output SHA-256 values stored in `data/dataset_manifest.json`.
- Lexical feature extraction and an offline held-out benchmark of Logistic Regression, linear SVM, and Random Forest. The selected model is persisted as `models/phishing_model.joblib` with `reports/model_metrics.json`.
- `POST /predict` and `GET /healthz` FastAPI endpoints.
- Optional SSL/TLS, DNS, WHOIS, and HTTP/HTML enrichment with bounded timeouts, a retry policy, cache, no redirects, and private-network target blocking.
- Tests, pinned dependencies, Docker health checks, structured JSON logs, and GitHub Actions CI.

## Security model for live enrichment

Feature enrichment can cause the server to contact user-supplied URLs, so it is opt-in (`include_live_features: true`) and deliberately constrained. Before resolving DNS, opening TLS, or making HTTP requests, the service accepts only HTTP(S) URLs on ports 80/443 and rejects credentials, loopback, private, link-local, multicast, reserved, and mixed DNS results. HTTP redirects are disabled; response bodies are capped at 64 KiB; every enrichment source has a strict timeout and errors are surfaced as unavailable rather than converted into a phishing verdict.

This reduces SSRF risk but should be deployed behind egress filtering and a DNS resolver that protects against DNS rebinding. Never point it at internal networks.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt -e .

# Builds a fresh 25k phishing + 25k legitimate URL dataset and version manifest.
python scripts/build_dataset.py

# Evaluates all three classifiers on a hostname-grouped held-out test set.
python scripts/train.py

pytest
uvicorn app:app --host 0.0.0.0 --port 8000
```

The interactive API contract is available at `http://localhost:8000/docs`.

```bash
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com/login","include_live_features":false}'
```

Use `docker compose up --build` to run the production-like container. The container expects `models/phishing_model.joblib`, produced by the training command.

## Data and model reproducibility

The dataset build stores a source snapshot manifest (timestamps and SHA-256s) beside the generated CSV. This makes a build auditable even though both upstream feeds change over time. `scripts/train.py` uses a fixed random seed and `GroupShuffleSplit` by hostname, avoiding the common leakage where multiple URLs from one domain appear in both training and test sets.

The two feeds use different collection rules: phishing entries are full reported URLs while Tranco entries are popular domains. This creates source-selection bias, so the baseline deliberately excludes scheme and path-shape fields that perfectly distinguish those sources and marks the report **research-only**. `reports/model_metrics.json` contains precision, recall, F1, ROC-AUC, confusion matrices, feature names, split sizes, leakage warnings, and the model-selection rationale. The default selection rule is highest held-out F1, breaking ties on ROC-AUC. Results will vary as source snapshots change—do not claim a metric without citing the report committed with the model, and do not represent it as production validation until it is evaluated against an independently collected, source-balanced dataset.

## Latency claims

Run the following only after training:

```bash
python scripts/benchmark_api.py --runs 100
```

It reports p50 and p95 end-to-end latency for lexical-only predictions. Do not describe live enrichment as sub-second: DNS, TLS, WHOIS, and HTML retrieval rely on external systems and can exceed the configured timeouts. The response includes `latency_ms` so production measurements can be captured in logs.

## Repository layout

```text
src/phishing_detector/  API, security boundary, features, data builder, training
scripts/                reproducible data, training, and latency commands
data/                   labelled URL snapshot and dataset manifest
models/                 selected serialised model
reports/                held-out benchmark results
tests/                  API, feature, and SSRF validation tests
```

## Responsible use

This project is a decision-support tool, not a browser safety guarantee. A score is probabilistic and must not be the sole basis for blocking, enforcement, or security incident decisions. Treat all downloaded phishing URLs as potentially dangerous data; the pipeline never visits them during dataset build or model training.
