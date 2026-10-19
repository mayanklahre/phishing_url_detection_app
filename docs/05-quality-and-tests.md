# Quality and evaluation

## Evaluation report
- Dataset: **50,000 URLs** — 25,000 phishing and 25,000 legitimate.
- Split: hostname-grouped held-out evaluation to reduce host leakage.
- Split sizes: **40,196 training rows** and **9,804 test rows**.
- Features: nine lexical URL features.
- Selected-model results: **97.8% F1** and **99.7% ROC-AUC**.

These are research metrics for the committed data snapshot and split, not a production-security claim. Source-selection bias remains a documented limitation.

## Quality controls
- Source and output SHA-256 values are recorded in the dataset manifest.
- Tests cover API, lexical features, URL validation, and SSRF controls.
- Docker health checks, pinned dependencies, structured JSON logs, and GitHub Actions support reproducibility.
- Live enrichment is optional and independently surfaced, with bounded response size, no redirects, timeouts, retries, and private-network protections.

## Benchmark status
Run the API benchmark after training to capture real p50 and p95 lexical-only latency:

    python scripts/benchmark_api.py --runs 100

No p50/p95 result is documented until this command is run in a stated environment and the output is retained. Do not call live enrichment sub-second.
