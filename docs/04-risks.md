# Risks and mitigations

| Risk | Impact | Mitigation | Residual limit |
| --- | --- | --- | --- |
| Dataset source-selection bias | High | Document data sources, exclude trivially distinguishing source artefacts, publish research-only warning. | Held-out results are not independent production validation. |
| Hostname leakage | High | Use hostname-grouped held-out split. | Other correlations can remain. |
| SSRF through live enrichment | High | Opt-in only; protocol/port restrictions; block credentials and private/reserved addresses; no redirects; bounds/timeouts/retries. | Real deployment also needs egress filtering and DNS-rebinding protection. |
| Slow/unavailable external lookup | Medium | Separate enrichment status from lexical verdict; use timeouts, retries, cache, and error states. | External dependencies can still fail. |
| Misuse as a safety guarantee | High | Explain probabilistic/research-only limitation and prohibit sole automated blocking decision. | Users may still over-trust a score. |
| Model/data drift | Medium | Preserve manifest, retrain/evaluate on a documented schedule, and compare new source snapshots. | Retraining does not itself prove real-world validity. |
