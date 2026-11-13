"""History features built only from training rows.

Item rates and the shopper's past fit mix are allowed as inputs. The label
of the row being scored is not. Quality, length, and the review text are
not features: they are written after the fit is known.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

NUMERIC_FEATURES = (
    "height_in",
    "weight_lbs",
    "age",
    "bust_band",
    "cup_index",
    "size_index",
    "user_n",
    "user_p_small",
    "user_p_large",
    "item_n",
    "item_p_small",
    "item_p_large",
    "size_vs_item_median",
)

CATEGORICAL_FEATURES = ("category", "body_type", "source", "rented_for")

MODEL_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _rate(count: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return float(count) / float(total)


def _class_table(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    counts = (
        frame.groupby([key, "fit"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["small", "fit", "large"], fill_value=0)
    )
    counts["n"] = counts.sum(axis=1)
    return counts


def _loo_user_features(train: pd.DataFrame) -> pd.DataFrame:
    """Past mix for each training row, with that row removed."""
    totals = train.groupby("user_id").size().rename("user_n_all")
    small = train["fit"].eq("small").groupby(train["user_id"]).sum().rename("user_small_all")
    large = train["fit"].eq("large").groupby(train["user_id"]).sum().rename("user_large_all")
    stats = pd.concat([totals, small, large], axis=1)
    joined = train[["user_id", "fit"]].join(stats, on="user_id")
    n = joined["user_n_all"] - 1
    small_n = joined["user_small_all"] - joined["fit"].eq("small").astype(int)
    large_n = joined["user_large_all"] - joined["fit"].eq("large").astype(int)
    return pd.DataFrame(
        {
            "user_n": n.clip(lower=0).astype(float),
            "user_p_small": [_rate(s, t) for s, t in zip(small_n, n)],
            "user_p_large": [_rate(lg, t) for lg, t in zip(large_n, n)],
        },
        index=train.index,
    )


def _loo_item_features(train: pd.DataFrame) -> pd.DataFrame:
    totals = train.groupby("item_id").size().rename("item_n_all")
    small = train["fit"].eq("small").groupby(train["item_id"]).sum().rename("item_small_all")
    large = train["fit"].eq("large").groupby(train["item_id"]).sum().rename("item_large_all")
    stats = pd.concat([totals, small, large], axis=1)
    joined = train[["item_id", "fit"]].join(stats, on="item_id")
    n = joined["item_n_all"] - 1
    small_n = joined["item_small_all"] - joined["fit"].eq("small").astype(int)
    large_n = joined["item_large_all"] - joined["fit"].eq("large").astype(int)
    return pd.DataFrame(
        {
            "item_n": n.clip(lower=0).astype(float),
            "item_p_small": [_rate(s, t) for s, t in zip(small_n, n)],
            "item_p_large": [_rate(lg, t) for lg, t in zip(large_n, n)],
        },
        index=train.index,
    )


def item_reference(train: pd.DataFrame) -> dict:
    """Aggregates a scorer can apply to a new row. Built from train only."""
    counts = _class_table(train, "item_id")
    fit_rows = train[train["fit"].eq("fit")]
    item_median = fit_rows.groupby("item_id")["size_index"].median()
    category_median = fit_rows.groupby("category")["size_index"].median()
    global_median = float(fit_rows["size_index"].median()) if len(fit_rows) else 0.0
    items = {}
    for item_id, row in counts.iterrows():
        items[str(item_id)] = {
            "n": int(row["n"]),
            "p_small": _rate(row["small"], row["n"]),
            "p_large": _rate(row["large"], row["n"]),
            "median_fit_size": float(item_median[item_id]) if item_id in item_median.index else None,
        }
    return {
        "items": items,
        "category_median_fit_size": {str(k): float(v) for k, v in category_median.items()},
        "global_median_fit_size": global_median,
        "category_mode_fit_size": {
            str(cat): float(series.mode().iloc[0])
            for cat, series in fit_rows.groupby("category")["size_index"]
            if len(series)
        },
    }


def _median_for(item_id: str, category: str, reference: dict) -> float:
    item = reference["items"].get(str(item_id))
    if item and item["median_fit_size"] is not None:
        return float(item["median_fit_size"])
    if category in reference["category_median_fit_size"]:
        return float(reference["category_median_fit_size"][category])
    return float(reference["global_median_fit_size"])


def _apply_reference(frame: pd.DataFrame, reference: dict, loo_items: pd.DataFrame | None) -> pd.DataFrame:
    out = frame.copy()
    out["cup_index"] = out["cup"].map(lambda cup: _cup(cup))
    if loo_items is None:
        stats = out["item_id"].map(lambda item: reference["items"].get(str(item)))
        out["item_n"] = [float(row["n"]) if isinstance(row, dict) else 0.0 for row in stats]
        out["item_p_small"] = [float(row["p_small"]) if isinstance(row, dict) else 0.0 for row in stats]
        out["item_p_large"] = [float(row["p_large"]) if isinstance(row, dict) else 0.0 for row in stats]
    else:
        out["item_n"] = loo_items["item_n"]
        out["item_p_small"] = loo_items["item_p_small"]
        out["item_p_large"] = loo_items["item_p_large"]
    medians = [
        _median_for(item, cat, reference)
        for item, cat in zip(out["item_id"], out["category"])
    ]
    out["item_median_fit_size"] = medians
    out["size_vs_item_median"] = out["size_index"] - out["item_median_fit_size"]
    return out


def _cup(cup) -> float:
    from fit_finder.data.clean import cup_to_index

    value = cup_to_index(None if cup == "unknown" else cup)
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    return float(value)


def add_features(
    train: pd.DataFrame,
    frame: pd.DataFrame,
    reference: dict | None = None,
    *,
    leave_one_out: bool = False,
) -> pd.DataFrame:
    """Attach history features.

    `leave_one_out` is for the training table, so a row's own label does not
    enter its user or item rate. Validation and test use the full training
    aggregates. Those rows are not in `train`.
    """
    reference = reference or item_reference(train)
    same = leave_one_out
    if same:
        user = _loo_user_features(train)
        item = _loo_item_features(train)
        out = _apply_reference(frame, reference, item)
        out["user_n"] = user["user_n"]
        out["user_p_small"] = user["user_p_small"]
        out["user_p_large"] = user["user_p_large"]
        return out
    user_counts = _class_table(train, "user_id")
    out = _apply_reference(frame, reference, None)
    mapped = out["user_id"].map(lambda user: user_counts.loc[user].to_dict() if user in user_counts.index else None)
    out["user_n"] = [float(row["n"]) if isinstance(row, dict) else 0.0 for row in mapped]
    out["user_p_small"] = [
        _rate(row["small"], row["n"]) if isinstance(row, dict) else 0.0 for row in mapped
    ]
    out["user_p_large"] = [
        _rate(row["large"], row["n"]) if isinstance(row, dict) else 0.0 for row in mapped
    ]
    return out
