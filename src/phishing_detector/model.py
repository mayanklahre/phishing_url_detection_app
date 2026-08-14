from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .features import MODEL_FEATURES, lexical_features


class ModelNotAvailable(RuntimeError):
    pass


@dataclass
class LoadedModel:
    estimator: Any
    feature_names: list[str]
    model_name: str
    model_version: str
    metrics: dict[str, float]

    def predict(self, url: str) -> tuple[int, float, dict[str, float]]:
        features = lexical_features(url)
        frame = pd.DataFrame([[features[name] for name in self.feature_names]], columns=self.feature_names)
        probability = float(self.estimator.predict_proba(frame)[0, 1])
        return int(probability >= 0.5), probability, features


def load_model(path: Path) -> LoadedModel:
    if not path.exists():
        raise ModelNotAvailable(f"model artifact is missing: {path}")
    artifact = joblib.load(path)
    feature_names = artifact.get("feature_names", MODEL_FEATURES)
    return LoadedModel(
        estimator=artifact["estimator"],
        feature_names=feature_names,
        model_name=artifact["model_name"],
        model_version=artifact["model_version"],
        metrics=artifact.get("metrics", {}),
    )
