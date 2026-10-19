# Requirements and acceptance criteria

| ID | User story | Acceptance criteria |
| --- | --- | --- |
| RQ-01 | As a developer, I can build a reproducible labelled dataset. | The build creates 25,000 phishing plus 25,000 legitimate URLs and records source/output SHA-256 values in the manifest. |
| RQ-02 | As a researcher, I can train and compare lexical classifiers. | Logistic Regression, linear SVM, and Random Forest are evaluated using a hostname-grouped held-out split and a documented selection rule. |
| RQ-03 | As an API client, I can obtain lexical prediction safely. | POST predict validates URL input and returns lexical result plus latency metadata. |
| RQ-04 | As an API client, I can opt into external enrichment. | TLS, DNS, WHOIS, and HTML enrichment is optional, bounded, and separately reported from the lexical score. |
| RQ-05 | As an operator, I am protected from obvious SSRF paths. | Only HTTP(S) on ports 80/443 is accepted; credentials/private/loopback/link-local/multicast/reserved targets and redirects are rejected; timeouts and response limits apply. |
| RQ-06 | As a reviewer, I can reproduce reported evaluation. | Train/test sizes, metrics, data limitations, model artefacts, tests, and commands are documented. |
