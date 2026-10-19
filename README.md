# Phishing URL Detection API

**Solo project | Originally built in 2024; repository published August 2026**

## Problem
A user or integrating application needs a fast, transparent initial risk signal for a URL. A classifier should not be presented as a browser-safety guarantee or the sole basis for an enforcement decision.

## Who it is for
Security-aware developers evaluating a research URL-classification API and its optional, constrained network-enrichment capability.

## Goal and success criteria
Build a reproducible lexical URL classifier with a documented dataset manifest, held-out evaluation, FastAPI endpoint, and optional enrichment that is constrained against obvious SSRF paths.

## Scope
**In:** 50,000-row reproducible data build, lexical feature extraction, model evaluation, FastAPI, optional DNS/TLS/WHOIS/HTML enrichment, SSRF controls, tests, Docker, and CI.

**Out:** a guarantee that any URL is safe/malicious, automatic blocking, enterprise threat intelligence, and production network security operations.

## Key decisions
- Lexical-only prediction is the default for predictable local scoring.
- Live enrichment is opt-in and independently reported because it depends on outside systems.
- SHA-256 manifest records the changing data-source snapshot.
- Hostname-grouped split reduces train/test host leakage.
- Cache, URL/DNS restrictions, no redirects, response bounds, and timeouts mitigate enrichment risk.

See the [decision log](docs/03-decision-log.md).

## Outcome
The selected model was evaluated on a hostname-grouped held-out split of **40,196 training** and **9,804 test** rows from a balanced **50,000-URL** dataset. It reached **97.8% F1** and **99.7% ROC-AUC** on that research evaluation. Results are not production validation and should be read with the documented source-selection-bias limitation.

## Risks and mitigations
Key risks are source bias, host leakage, SSRF, slow/unavailable enrichment, model drift, and over-trust in a score. See [risks](docs/04-risks.md).

## How to run
Requires Python 3.11+.

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt -e .
    python scripts/build_dataset.py
    python scripts/train.py
    pytest
    uvicorn app:app --host 0.0.0.0 --port 8000

For a production-like local container:

    docker compose up --build

Run a lexical-only benchmark after training:

    python scripts/benchmark_api.py --runs 100

## Next steps
- Record and publish real p50/p95 lexical-only latency from a stated environment.
- Evaluate against an independently collected, source-balanced dataset.
- Add authenticated access, rate limits, egress filtering, protected DNS, and monitoring for any deployment.
- Monitor data/model drift with retained manifests and repeatable evaluation.

## Documentation
- [Brief](docs/01-brief.md)
- [Requirements](docs/02-requirements.md)
- [Decision log](docs/03-decision-log.md)
- [Risks](docs/04-risks.md)
- [Quality and evaluation](docs/05-quality-and-tests.md)
- [Retrospective](docs/06-retrospective.md)
