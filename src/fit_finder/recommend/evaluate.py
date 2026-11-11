"""Offline hit rate for the content ranker.

For a held-out review labeled fit, the item the person reviewed is the
positive. The candidate set is that item plus random other items in the
same category. Hit rate at 10 asks whether the positive lands in the top 10.
This is a ranking check, not a shopper experiment.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fit_finder.recommend.catalog import build_catalog
from fit_finder.recommend.rank import rank_items


def hit_rate_at_k(
    reviews: pd.DataFrame,
    *,
    k: int = 10,
    negatives: int = 49,
    max_queries: int = 800,
    seed: int = 7,
) -> dict:
    catalog = build_catalog(reviews)
    positives = reviews[reviews["fit"].eq("fit")]
    if positives.empty:
        return {"hit_rate": 0.0, "mrr": 0.0, "n": 0, "k": k}
    rng = np.random.default_rng(seed)
    take = min(max_queries, len(positives))
    chosen = positives.iloc[rng.choice(len(positives), size=take, replace=False)]
    by_category = {cat: frame for cat, frame in catalog.groupby("category")}
    hits = []
    reciprocal = []
    for row in chosen.itertuples(index=False):
        pool = by_category.get(row.category)
        if pool is None or len(pool) < 2:
            continue
        others = pool[pool["item_id"] != row.item_id]
        if others.empty:
            continue
        n_neg = min(negatives, len(others))
        sample = others.sample(n=n_neg, random_state=int(rng.integers(0, 1_000_000)))
        positive = pool[pool["item_id"].eq(row.item_id)]
        candidates = pd.concat([positive, sample], ignore_index=True)
        ranked = rank_items(
            candidates,
            category=row.category,
            size_index=float(row.size_index),
            limit=max(k, len(candidates)),
        )
        ids = ranked["item_id"].tolist()
        if row.item_id in ids[:k]:
            hits.append(1.0)
        else:
            hits.append(0.0)
        if row.item_id in ids:
            reciprocal.append(1.0 / (ids.index(row.item_id) + 1))
        else:
            reciprocal.append(0.0)
    n = len(hits)
    return {
        "hit_rate": float(np.mean(hits)) if n else 0.0,
        "mrr": float(np.mean(reciprocal)) if n else 0.0,
        "n": n,
        "k": k,
        "negatives": negatives,
        "label": "held-out fit review ranked among same-category items",
    }
