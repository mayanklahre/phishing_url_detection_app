# Decision log

| ID | Decision | Options considered | Choice and rationale | Consequence |
| --- | --- | --- | --- | --- |
| D-01 | Default prediction inputs | Lexical only; always live enrichment | **Lexical-only default** makes the core path local, fast, reproducible, and independent of outside network signals. | It cannot use reputation/hosting signals by default. |
| D-02 | Optional enrichment | No enrichment; unrestricted requests; opt-in constrained enrichment | **Opt-in constrained enrichment** adds DNS/TLS/WHOIS/HTML context while exposing failure state separately. | It is slower and must never be described as sub-second. |
| D-03 | Dataset provenance | Unrecorded downloads; fixed packaged data; SHA-256 manifest | **SHA-256 manifest** records source/output snapshot information to make a changing-source build auditable. | It does not eliminate source-selection bias. |
| D-04 | Split strategy | Random row split; hostname-grouped split | **Hostname-grouped split** prevents URLs from the same hostname appearing in both train and test sets. | Results can differ from an easier random split. |
| D-05 | Network controls | Direct user URL fetch; bounded/cached fetch | **Caching plus strict URL/DNS constraints** reduce repeated calls and SSRF exposure. | Defence in depth still needs protected egress/DNS in deployment. |
