"""The most-common-class fit baseline, and the most-common-size recommender.

"Most common" is the right dumb answer on this data: about seven in ten
reviews say the item fit. A model that cannot beat that accuracy still has
to beat it on log loss, because the product shows a confidence, not a
majority label.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CLASSES = ("small", "fit", "large")


class MajorityBaseline:
    """Predict the training mix for every row. Implements the sklearn shape."""

    def __init__(self) -> None:
        self.classes_ = np.array(CLASSES)
        self.proba_ = np.array([1 / 3, 1 / 3, 1 / 3])
        self.majority_ = "fit"

    def fit(self, _X, y) -> "MajorityBaseline":
        labels = pd.Series(list(y))
        shares = labels.value_counts(normalize=True)
        self.majority_ = str(shares.idxmax())
        self.proba_ = np.array([float(shares.get(name, 0.0)) for name in CLASSES])
        return self

    def predict_proba(self, X) -> np.ndarray:
        return np.tile(self.proba_, (len(X), 1))

    def predict(self, X) -> np.ndarray:
        return np.full(len(X), self.majority_)


def most_common_fit_size(train: pd.DataFrame) -> pd.Series:
    """Modal size among training reviews that said the item fit, by category."""
    fit_rows = train[train["fit"].eq("fit")]
    modes = {}
    for category, series in fit_rows.groupby("category")["size_index"]:
        if len(series) == 0:
            continue
        modes[category] = float(series.mode().iloc[0])
    return pd.Series(modes, name="mode_fit_size")
