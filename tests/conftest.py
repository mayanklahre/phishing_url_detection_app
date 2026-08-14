from __future__ import annotations

from pathlib import Path

import pytest
from sklearn.dummy import DummyClassifier

from phishing_detector.features import LEXICAL_FEATURES
from phishing_detector.model import LoadedModel


@pytest.fixture
def loaded_model() -> LoadedModel:
    estimator = DummyClassifier(strategy="constant", constant=0)
    estimator.fit([[0.0] * len(LEXICAL_FEATURES), [1.0] * len(LEXICAL_FEATURES)], [0, 1])
    return LoadedModel(estimator, LEXICAL_FEATURES, "test_model", "test-v1", {"f1": 1.0})
