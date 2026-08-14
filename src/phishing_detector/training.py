from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import GroupShuffleSplit

from .features import LEXICAL_FEATURES, MODEL_FEATURES, lexical_features

RANDOM_SEED = 42


def _domain(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def _feature_frame(urls: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([lexical_features(url) for url in urls], columns=LEXICAL_FEATURES)


def _metrics(y_true: pd.Series, probabilities: np.ndarray) -> tuple[dict[str, float], list[list[int]]]:
    prediction = (probabilities >= 0.5).astype(int)
    return (
        {
            "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 6),
            "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 6),
            "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 6),
            "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 6),
        },
        confusion_matrix(y_true, prediction, labels=[0, 1]).tolist(),
    )


def _quality_warnings(features: pd.DataFrame, labels: pd.Series) -> list[str]:
    warnings = [
        "Research-only baseline: labels come from separate phishing and popularity feeds. "
        "A held-out split cannot remove source-selection bias; validate on an independently collected dataset before production use."
    ]
    for name in LEXICAL_FEATURES:
        grouped = features.groupby(labels)[name].nunique()
        if grouped.get(0, 2) == 1 and grouped.get(1, 2) == 1 and features.loc[labels == 0, name].iloc[0] != features.loc[labels == 1, name].iloc[0]:
            warnings.append(f"Excluded from model: {name} perfectly separates source labels in this snapshot.")
    return warnings


def train_and_select(dataset: Path, manifest: Path, artifact: Path, report: Path, minimum_rows: int = 50_000) -> dict[str, object]:
    data = pd.read_csv(dataset)
    if not {"url", "label"}.issubset(data.columns):
        raise ValueError("dataset must contain url,label columns")
    data = data.dropna(subset=["url", "label"]).drop_duplicates("url").copy()
    data["label"] = data["label"].astype(int)
    if len(data) < minimum_rows:
        raise ValueError(f"dataset has {len(data):,} rows; at least {minimum_rows:,} are required")
    if set(data["label"].unique()) != {0, 1}:
        raise ValueError("dataset must contain both labels 0 and 1")
    groups = data["url"].map(_domain)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_SEED)
    train_index, test_index = next(splitter.split(data, data["label"], groups=groups))
    train_data, test_data = data.iloc[train_index], data.iloc[test_index]
    full_train, full_test = _feature_frame(train_data["url"]), _feature_frame(test_data["url"])
    x_train, x_test = full_train[MODEL_FEATURES], full_test[MODEL_FEATURES]
    y_train, y_test = train_data["label"], test_data["label"]
    candidates = {
        "logistic_regression": Pipeline([("scale", StandardScaler()), ("model", LogisticRegression(max_iter=2_000, class_weight="balanced", random_state=RANDOM_SEED))]),
        "svm": Pipeline([("scale", StandardScaler()), ("model", SVC(kernel="linear", probability=True, class_weight="balanced", random_state=RANDOM_SEED))]),
        "random_forest": RandomForestClassifier(n_estimators=350, min_samples_leaf=2, n_jobs=-1, class_weight="balanced", random_state=RANDOM_SEED),
    }
    results: dict[str, dict[str, object]] = {}
    fitted: dict[str, object] = {}
    for name, estimator in candidates.items():
        estimator.fit(x_train, y_train)
        probabilities = estimator.predict_proba(x_test)[:, 1]
        metrics, matrix = _metrics(y_test, probabilities)
        results[name] = {"metrics": metrics, "confusion_matrix": matrix}
        fitted[name] = estimator
    best_name = max(results, key=lambda name: (results[name]["metrics"]["f1"], results[name]["metrics"]["roc_auc"]))
    dataset_info = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"sha256": hashlib.sha256(dataset.read_bytes()).hexdigest()}
    model_version = f"{best_name}-{hashlib.sha256((dataset_info['sha256'] + best_name).encode()).hexdigest()[:12]}"
    summary: dict[str, object] = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "feature_set": MODEL_FEATURES,
        "split": {"strategy": "GroupShuffleSplit by hostname", "train_rows": len(train_data), "test_rows": len(test_data), "test_size": 0.2},
        "dataset": dataset_info,
        "models": results,
        "selected_model": best_name,
        "selection_rationale": "Highest held-out F1; ROC-AUC breaks ties.",
        "model_version": model_version,
        "quality_warnings": _quality_warnings(_feature_frame(data["url"]), data["label"]),
    }
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"estimator": fitted[best_name], "feature_names": MODEL_FEATURES, "model_name": best_name, "model_version": model_version, "metrics": results[best_name]["metrics"], "training_summary": summary}, artifact, compress=3)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark phishing classifiers and persist the selected model.")
    parser.add_argument("--dataset", type=Path, default=Path("data/urls.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("data/dataset_manifest.json"))
    parser.add_argument("--artifact", type=Path, default=Path("models/phishing_model.joblib"))
    parser.add_argument("--report", type=Path, default=Path("reports/model_metrics.json"))
    parser.add_argument("--minimum-rows", type=int, default=50_000)
    args = parser.parse_args()
    print(json.dumps(train_and_select(args.dataset, args.manifest, args.artifact, args.report, args.minimum_rows), indent=2))


if __name__ == "__main__":
    main()
