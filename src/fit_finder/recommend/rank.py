"""Rank items a shopper is more likely to say fit.

The score is a weighted sum of the item's historical fit rate and how close
its usual fit size is to the size the shopper is considering. It is not a
learned collaborative filter. Session 9 is where that comparison lives, on
synthetic purchases, because the H&M file is not in this repo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fit_finder.recommend.catalog import price_band


def _closeness(median_size: pd.Series, target: float) -> pd.Series:
    return 1.0 / (1.0 + (median_size - target).abs())


def rank_items(
    catalog: pd.DataFrame,
    *,
    category: str,
    size_index: float,
    limit: int = 5,
    exclude_item_id: str | None = None,
    price: float | None = None,
    color: str | None = None,
) -> pd.DataFrame:
    """Return the top items in a category.

    `price` filters to the illustrative band for the category when one is
    defined. Items themselves have no observed price. `color` is applied
    only when the catalog row has a color, which the UCSD aggregate does not.
    """
    pool = catalog[catalog["category"].eq(str(category).strip().lower())].copy()
    if exclude_item_id:
        pool = pool[pool["item_id"] != exclude_item_id]
    if price is not None:
        band = price_band(category)
        if band is not None and not (band[0] <= float(price) <= band[1]):
            # The caller's price is outside the illustrative band. We still
            # rank the category, and we record that the filter did not apply
            # a cut, because there is no item price to cut on.
            pool["price_filter"] = "illustrative_band_mismatch_no_item_price"
        else:
            pool["price_filter"] = "illustrative_band_only"
    else:
        pool["price_filter"] = "not_requested"
    if color and "color" in pool.columns and pool["color"].astype(str).str.len().gt(0).any():
        wanted = str(color).strip().lower()
        colored = pool[pool["color"].astype(str).str.lower().eq(wanted)]
        if len(colored):
            pool = colored
    if pool.empty:
        return pool
    fit_rate = pool["fit_rate"].astype(float)
    close = _closeness(pool["median_fit_size"].astype(float), float(size_index))
    # A handful of reviews should not outrank a well-reviewed item on noise.
    support = np.log1p(pool["n_reviews"].astype(float))
    support = support / support.max() if float(support.max()) else support
    pool["score"] = 0.65 * fit_rate + 0.25 * close + 0.10 * support
    pool["why"] = "historical fit rate, size closeness, and review support"
    columns = [
        "item_id",
        "source",
        "category",
        "n_reviews",
        "fit_rate",
        "median_fit_size",
        "score",
        "why",
        "price_filter",
    ]
    return pool.sort_values(["score", "n_reviews"], ascending=False).head(limit)[columns].reset_index(drop=True)
