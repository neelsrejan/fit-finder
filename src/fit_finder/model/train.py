"""Fit three predictors and keep the one with the best validation log loss.

The candidates are a most-common-class baseline, L2 logistic regression, and
LightGBM. The learned models are calibrated on the validation split with
Platt scaling. Test rows are scored once, after the choice is made.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from fit_finder.model.baselines import CLASSES, MajorityBaseline
from fit_finder.model.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, add_features, item_reference
from fit_finder.model.split import assign_split

try:
    from lightgbm import LGBMClassifier
except ImportError:  # pragma: no cover - installed in the project env
    LGBMClassifier = None

try:
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.frozen import FrozenEstimator
except ImportError:  # pragma: no cover
    CalibratedClassifierCV = None
    FrozenEstimator = None


def preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric, list(NUMERIC_FEATURES)),
            ("cat", categorical, list(CATEGORICAL_FEATURES)),
        ]
    )


def _matrix(pre: ColumnTransformer, frame: pd.DataFrame, fit: bool) -> np.ndarray:
    columns = frame.loc[:, list(NUMERIC_FEATURES + CATEGORICAL_FEATURES)]
    if fit:
        return pre.fit_transform(columns)
    return pre.transform(columns)


def _align(model, proba: np.ndarray) -> np.ndarray:
    index = {str(label): i for i, label in enumerate(model.classes_)}
    # MajorityBaseline stores class names. Sklearn estimators may store them too.
    # Integer-coded estimators are not used here.
    return np.column_stack([proba[:, index[name]] for name in CLASSES])


def _metrics(y_true: np.ndarray, proba: np.ndarray) -> dict:
    pred = np.array(CLASSES)[np.argmax(proba, axis=1)]
    # sklearn one-hot encodes labels in lexicographic order and does not
    # reorder the probability columns to match a custom label list.
    lex = sorted(CLASSES)
    column = [list(CLASSES).index(name) for name in lex]
    return {
        "log_loss": float(log_loss(y_true, proba[:, column], labels=lex)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, labels=list(CLASSES), average="macro")),
        "n": int(len(y_true)),
    }


def _ece(y_true: np.ndarray, proba: np.ndarray, bins: int = 10) -> float:
    """Expected calibration error of the top-class confidence."""
    confidence = proba.max(axis=1)
    pred = np.array(CLASSES)[np.argmax(proba, axis=1)]
    correct = pred == np.asarray(y_true)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (confidence >= low) & (confidence < high if high < 1 else confidence <= high)
        if not np.any(mask):
            continue
        gap = abs(float(correct[mask].mean()) - float(confidence[mask].mean()))
        total += gap * float(mask.mean())
    return float(total)


def _calibrate(model, x_val, y_val):
    if FrozenEstimator is None or CalibratedClassifierCV is None:
        return model
    if len(np.unique(y_val)) < 2 or len(y_val) < 30:
        return model
    calibrated = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
    calibrated.fit(x_val, y_val)
    return calibrated


def _logistic():
    return LogisticRegression(max_iter=500, C=1.0)


def _lightgbm():
    if LGBMClassifier is None:
        raise RuntimeError("lightgbm is not installed")
    return LGBMClassifier(
        objective="multiclass",
        n_estimators=180,
        learning_rate=0.08,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=7,
        verbose=-1,
    )


def _category_accuracy(frame: pd.DataFrame, pred: np.ndarray) -> list[dict]:
    table = frame[["category"]].copy()
    table["hit"] = pred == frame["fit"].to_numpy()
    rows = []
    for category, group in table.groupby("category"):
        rows.append(
            {
                "category": str(category),
                "n": int(len(group)),
                "accuracy": float(group["hit"].mean()),
            }
        )
    rows.sort(key=lambda row: row["n"], reverse=True)
    return rows


def direction_hit(actual: str, ordered: float, recommended: float) -> bool:
    """Whether the size suggestion moves the right way.

    "small" means the garment was small, so a larger size is the correction.
    "large" means the garment was large, so a smaller size is the correction.
    "fit" means the ordered size should stay.
    """
    if actual == "fit":
        return recommended == ordered
    if actual == "small":
        return recommended > ordered
    if actual == "large":
        return recommended < ordered
    return False


def score_size_policy(model, pre: ColumnTransformer, featured: pd.DataFrame, offsets=(-2, -1, 0, 1, 2)) -> np.ndarray:
    """Pick the nearby size whose calibrated P(fit) is highest."""
    blocks = []
    for offset in offsets:
        trial = featured.copy()
        trial["size_index"] = featured["size_index"] + offset
        trial["size_vs_item_median"] = trial["size_index"] - featured["item_median_fit_size"]
        blocks.append(trial)
    stacked = pd.concat(blocks, ignore_index=True)
    proba = _align(model, model.predict_proba(_matrix(pre, stacked, fit=False)))
    fit_col = CLASSES.index("fit")
    p_fit = proba[:, fit_col].reshape(len(offsets), len(featured)).T
    best = np.argmax(p_fit, axis=1)
    return featured["size_index"].to_numpy() + np.array(offsets)[best]


def prepare(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    work = frame.reset_index(drop=True).copy()
    work["split"] = assign_split(work)
    train = work[work["split"].eq("train")].copy()
    val = work[work["split"].eq("val")].copy()
    test = work[work["split"].eq("test")].copy()
    reference = item_reference(train)
    train = add_features(train, train, reference, leave_one_out=True)
    val = add_features(train, val, reference, leave_one_out=False)
    test = add_features(train, test, reference, leave_one_out=False)
    # add_features(train, val) uses the train argument for user history.
    # Passing the already-featured train frame is fine: fit and ids are unchanged.
    return train, val, test, reference


def train_models(frame: pd.DataFrame, lightgbm_rounds: int | None = None) -> dict:
    train, val, test, reference = prepare(frame)
    pre = preprocessor()
    x_train = _matrix(pre, train, fit=True)
    x_val = _matrix(pre, val, fit=False)
    x_test = _matrix(pre, test, fit=False)
    y_train = train["fit"].to_numpy()
    y_val = val["fit"].to_numpy()
    y_test = test["fit"].to_numpy()

    candidates = {"majority": MajorityBaseline()}
    candidates["logistic"] = _logistic()
    gbm = _lightgbm()
    if lightgbm_rounds is not None:
        gbm.set_params(n_estimators=lightgbm_rounds)
    candidates["lightgbm"] = gbm

    fitted = {}
    val_scores = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        if name != "majority":
            model = _calibrate(model, x_val, y_val)
        proba = _align(model, model.predict_proba(x_val))
        val_scores[name] = _metrics(y_val, proba)
        fitted[name] = model

    chosen = min(val_scores, key=lambda name: val_scores[name]["log_loss"])
    test_scores = {}
    test_proba = {}
    for name, model in fitted.items():
        proba = _align(model, model.predict_proba(x_test))
        test_proba[name] = proba
        row = _metrics(y_test, proba)
        row["ece"] = _ece(y_test, proba)
        test_scores[name] = row

    chosen_model = fitted[chosen]
    recommended = score_size_policy(chosen_model, pre, test)
    directional = [
        direction_hit(actual, ordered, rec)
        for actual, ordered, rec in zip(test["fit"], test["size_index"], recommended)
    ]
    from fit_finder.model.baselines import most_common_fit_size

    modes = most_common_fit_size(train)
    baseline_size = test["category"].map(modes)
    global_mode = float(train.loc[train["fit"].eq("fit"), "size_index"].mode().iloc[0])
    baseline_size = baseline_size.fillna(global_mode)
    baseline_hits = [
        direction_hit(actual, ordered, rec)
        for actual, ordered, rec in zip(test["fit"], test["size_index"], baseline_size)
    ]
    pred = np.array(CLASSES)[np.argmax(test_proba[chosen], axis=1)]
    by_category = _category_accuracy(test, pred)

    return {
        "preprocessor": pre,
        "models": fitted,
        "chosen_model": chosen,
        "reference": reference,
        "validation": val_scores,
        "test": test_scores,
        "directional_accuracy": float(np.mean(directional)) if directional else 0.0,
        "most_common_size_directional_accuracy": float(np.mean(baseline_hits)) if baseline_hits else 0.0,
        "per_category": by_category[:15],
        "split_counts": {
            "train": int(len(train)),
            "val": int(len(val)),
            "test": int(len(test)),
        },
        "test_frame": test,
        "test_proba": test_proba[chosen],
    }


def bundle_from_result(result: dict) -> dict:
    name = result["chosen_model"]
    return {
        "preprocessor": result["preprocessor"],
        "model": result["models"][name],
        "model_name": name,
        "classes": list(CLASSES),
        "reference": _slim_reference(result["reference"]),
        "metrics": public_metrics(result),
    }


def _slim_reference(reference: dict) -> dict:
    """Drop nothing needed at score time, but keep the dict JSON-friendly."""
    return reference


def public_metrics(result: dict) -> dict:
    return {
        "chosen_model": result["chosen_model"],
        "selection_rule": "lowest validation log loss after calibration",
        "split_counts": result["split_counts"],
        "validation": result["validation"],
        "test": result["test"],
        "directional_accuracy": result["directional_accuracy"],
        "most_common_size_directional_accuracy": result["most_common_size_directional_accuracy"],
        "per_category": result["per_category"],
        "classes": list(CLASSES),
    }


def save_bundle(bundle: dict, path: Path) -> None:
    import joblib

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)


def write_metrics(metrics: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2) + "\n")


def heldout_scores(result: dict, limit: int = 4000, seed: int = 7) -> pd.DataFrame:
    test = result["test_frame"]
    proba = result["test_proba"]
    take = min(limit, len(test))
    rng = np.random.default_rng(seed)
    chosen = np.sort(rng.choice(len(test), size=take, replace=False))
    pred = np.array(CLASSES)[np.argmax(proba[chosen], axis=1)]
    frame = pd.DataFrame(
        {
            "source": test["source"].to_numpy()[chosen],
            "category": test["category"].to_numpy()[chosen],
            "fit_actual": test["fit"].to_numpy()[chosen],
            "fit_pred": pred,
            "p_small": proba[chosen, 0],
            "p_fit": proba[chosen, 1],
            "p_large": proba[chosen, 2],
            "confidence": proba[chosen].max(axis=1),
            "model": result["chosen_model"],
        }
    )
    return frame
