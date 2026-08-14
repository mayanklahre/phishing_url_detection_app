# Dataset contract

`urls.csv` is a versioned, labelled dataset created by `python scripts/build_dataset.py`.
It contains exactly two columns: `url` and `label` (`1` = phishing, `0` = legitimate). The companion `dataset_manifest.json` records the build time, record count, source snapshot checksums, and the resulting CSV SHA-256.

The builder reads phishing URL labels from Phishing.Database and popular domains from Tranco. It does **not** visit or execute any listed URL. Rebuild only in an isolated research environment; phishing URLs are malicious content.

The application trains on lexical features only. SSL/TLS, DNS, WHOIS, and HTML data are collected only when a caller explicitly opts into live enrichment, so the training dataset does not embed transient personal or network data.
