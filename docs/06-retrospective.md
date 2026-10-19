# Retrospective

**Retrospective documentation, written on 19 October 2026.** This reflects the completed solo repository and is not backdated project evidence.

## What worked
- Lexical-only prediction created a predictable local baseline.
- Hostname-grouped evaluation and SHA-256 provenance made the research setup more defensible than a casual random split.
- Optional enrichment was separated from the core result and designed with explicit SSRF safeguards.

## What was difficult
- High held-out metrics can be misleading when source datasets are collected differently.
- Live enrichment introduces latency and network risk that lexical-only prediction avoids.
- A safety score needs careful framing so it is not used as a final security decision.

## Improvements
- Run and publish a reproducible p50/p95 lexical-only benchmark.
- Evaluate against an independently collected, source-balanced dataset.
- Add deployment egress controls, protected DNS, monitoring, rate limits, and authentication.
- Track data drift and model performance over documented source snapshots.
