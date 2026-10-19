# v1.0.0 release notes

**Release notes prepared on 19 October 2026.**

## Shipped
- Reproducible 50,000-URL lexical classifier with source/output SHA-256 manifest.
- Hostname-grouped held-out evaluation, FastAPI API, optional constrained enrichment, tests, Docker, and CI.
- Selected research model: 97.8% F1 and 99.7% ROC-AUC on the committed evaluation setup.

## Known limits
- Metrics are research results, not production validation or a browser-safety guarantee.
- Live enrichment depends on external systems and must not be described as sub-second.
- p50/p95 lexical-only benchmark is pending.

## Handover
Repository includes training, evaluation, benchmark, test, container, security, and risk documentation.
