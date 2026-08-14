from phishing_detector.features import lexical_features


def test_lexical_features_are_deterministic() -> None:
    values = lexical_features("https://login-secure.example.com/a?next=1")
    assert values["uses_https"] == 1.0
    assert values["suspicious_token_count"] >= 2.0
    assert values["query_parameter_count"] == 1.0
