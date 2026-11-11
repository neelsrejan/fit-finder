"""Compare the Session 4 ranker with item-item CF on the synthetic fixture.

Both methods are scored on the same question: did a held-out synthetic
purchase land in the top 10? This is not a comparison on H&M customers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fit_finder.hm.adapter import SyntheticHMSource
from fit_finder.hm.cf import leave_one_out_hit_rate
from fit_finder.recommend.rank import rank_items


def content_hit_rate(source: SyntheticHMSource, k: int = 10) -> dict:
    articles = source.articles()
    transactions = source.transactions().sort_values(["user_id", "date", "item_id"])
    last = transactions.groupby("user_id", as_index=False).tail(1)
    catalog = articles.rename(columns={"fit_rate": "fit_rate"})
    catalog["n_reviews"] = 20
    catalog["median_fit_size"] = 8.0
    catalog["source"] = "synthetic"
    hits = []
    reciprocal = []
    for row in last.itertuples(index=False):
        article = articles.loc[articles["item_id"].eq(row.item_id)].iloc[0]
        ranked = rank_items(
            catalog,
            category=str(article["category"]),
            size_index=8.0,
            limit=k,
            exclude_item_id=None,
            color=str(article["color"]),
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
        "method": "content_fit_rate",
        "simulated_fixture": True,
    }


def compare(k: int = 3) -> dict:
    source = SyntheticHMSource()
    content = content_hit_rate(source, k=k)
    cf = leave_one_out_hit_rate(source.transactions(), k=k)
    return {
        "blocked": "H&M Kaggle file was not downloaded. Metrics are the synthetic fixture.",
        "content": content,
        "collaborative_filtering": cf,
        "note": (
            "Content ranking uses planted fit_rate and category. "
            "Collaborative filtering uses planted category preference in the purchases. "
            "Neither number is an H&M customer metric."
        ),
    }


def transactions_frame() -> pd.DataFrame:
    return SyntheticHMSource().transactions()
