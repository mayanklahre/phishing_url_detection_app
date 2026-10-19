# Project brief

**Project:** Phishing URL Detection API  
**Delivery:** Solo project. Originally built in 2024; repository published August 2026.

## Problem and users
A user or integrating application needs a fast initial risk signal for a URL. The intended user is a security-aware developer evaluating a research classifier, not a team seeking an automatic enforcement system.

## Goal and success criteria
Build a reproducible lexical URL classifier with an API, documented security boundary for optional network enrichment, and held-out evaluation. The research dataset contains 25,000 phishing and 25,000 legitimate URLs. The selected model was evaluated on a hostname-grouped held-out split.

## Scope
**In:** reproducible data build/manifest, lexical features, model training/evaluation, FastAPI, controlled optional enrichment, tests, containerisation, and CI.

**Out:** browser safety guarantee, automatic blocking/enforcement, ground-truth validation against every real-world URL, and production network security operations.
