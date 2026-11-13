"""Build an item catalog from fit reviews.

The UCSD files do not contain price or color. Price bands in this package
are illustrative category bands used only when a caller passes a price, and
they are labeled as such. Color is accepted on the request and ignored for
UCSD items, because the column does not exist.
"""

from __future__ import annotations

import pandas as pd

# Illustrative US dollar bands for a demo filter. These are not transaction
# prices from either dataset.
ILLUSTRATIVE_PRICE_BANDS = {
    "dress": (80, 180),
    "dresses": (80, 180),
    "gown": (120, 280),
    "romper": (60, 140),
    "jumpsuit": (70, 160),
    "jeans": (40, 120),
    "pants": (40, 120),
    "skirt": (40, 110),
    "top": (30, 90),
    "blouse": (35, 95),
    "sweater": (40, 120),
    "jacket": (70, 200),
    "coat": (90, 240),
}


def price_band(category: str) -> tuple[float, float] | None:
    return ILLUSTRATIVE_PRICE_BANDS.get(str(category).strip().lower())


def build_catalog(reviews: pd.DataFrame) -> pd.DataFrame:
    """One row per item. `fit_rate` is the share of reviews that said fit."""
    fit = reviews["fit"].eq("fit")
    grouped = reviews.groupby(["item_id", "source", "category"], as_index=False).agg(
        n_reviews=("fit", "size"),
        fit_rate=("fit", lambda s: float(s.eq("fit").mean())),
        median_fit_size=("size_index", "median"),
    )
    # median_fit_size above includes small and large reviews. Recompute it
    # on fit reviews only, which is the size shoppers said worked.
    fit_only = reviews[fit]
    medians = fit_only.groupby("item_id")["size_index"].median()
    grouped["median_fit_size"] = grouped["item_id"].map(medians)
    grouped["median_fit_size"] = grouped["median_fit_size"].fillna(grouped["median_fit_size"].median())
    grouped["price_source"] = "none"
    grouped["color"] = ""
    return grouped.sort_values("n_reviews", ascending=False).reset_index(drop=True)
