"""Score one shopper-item row with the saved bundle."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fit_finder.model.baselines import CLASSES
from fit_finder.model.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from fit_finder.model.train import _align, _matrix, direction_hit, score_size_policy


def load_bundle(path: Path) -> dict:
    import joblib

    return joblib.load(path)


def _blank_row() -> dict:
    row = {name: np.nan for name in NUMERIC_FEATURES}
    for name in CATEGORICAL_FEATURES:
        row[name] = "unknown"
    row["item_id"] = ""
    row["user_id"] = ""
    row["item_median_fit_size"] = np.nan
    row["cup"] = "unknown"
    return row


def describe_adjustment(actual_size: float, recommended: float) -> str:
    if recommended == actual_size:
        return "The ordered size has the highest calibrated probability of fit among the nearby sizes."
    if recommended > actual_size:
        return "A larger nearby size has a higher calibrated probability of fit."
    return "A smaller nearby size has a higher calibrated probability of fit."


def predict_one(bundle: dict, payload: dict) -> dict:
    """Fill history from the training aggregates and score the row.

    An unknown shopper gets zero history. That is the cold-start case, and
    the confidence should be read with that in mind.
    """
    reference = bundle["reference"]
    row = _blank_row()
    row["category"] = str(payload.get("category") or "unknown").strip().lower()
    row["body_type"] = str(payload.get("body_type") or "unknown").strip().lower()
    row["source"] = str(payload.get("source") or "unknown").strip().lower()
    row["rented_for"] = str(payload.get("rented_for") or "unknown").strip().lower()
    row["size_index"] = float(payload["size_index"])
    for key in ("height_in", "weight_lbs", "age", "bust_band", "cup_index"):
        if payload.get(key) is not None:
            row[key] = float(payload[key])
    item_id = str(payload.get("item_id") or "")
    item = reference["items"].get(item_id)
    if item:
        row["item_n"] = item["n"]
        row["item_p_small"] = item["p_small"]
        row["item_p_large"] = item["p_large"]
        median = item["median_fit_size"]
    else:
        row["item_n"] = 0.0
        row["item_p_small"] = 0.0
        row["item_p_large"] = 0.0
        median = reference["category_median_fit_size"].get(
            row["category"], reference["global_median_fit_size"]
        )
    row["item_median_fit_size"] = float(median)
    row["size_vs_item_median"] = row["size_index"] - row["item_median_fit_size"]
    if payload.get("user_n"):
        row["user_n"] = float(payload["user_n"])
        row["user_p_small"] = float(payload.get("user_p_small") or 0.0)
        row["user_p_large"] = float(payload.get("user_p_large") or 0.0)
    else:
        row["user_n"] = 0.0
        row["user_p_small"] = 0.0
        row["user_p_large"] = 0.0

    frame = pd.DataFrame([row])
    model = bundle["model"]
    proba = _align(model, model.predict_proba(_matrix(bundle["preprocessor"], frame, fit=False)))[0]
    label = CLASSES[int(np.argmax(proba))]
    recommended = float(score_size_policy(model, bundle["preprocessor"], frame)[0])
    return {
        "fit_class": label,
        "confidence": float(proba.max()),
        "probabilities": {name: float(value) for name, value in zip(CLASSES, proba)},
        "ordered_size": float(payload["size_index"]),
        "recommended_size": recommended,
        "size_note": describe_adjustment(float(payload["size_index"]), recommended),
        "model": bundle["model_name"],
        "calibrated": bundle["model_name"] != "majority",
        "history": "item" if item else "category_fallback",
    }


def explain_direction(actual_fit: str, ordered: float, recommended: float) -> bool:
    return direction_hit(actual_fit, ordered, recommended)
