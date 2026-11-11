"""Review-level split that keeps a shopper's earlier reviews in train.

ModCloth's public file has no review timestamp, so within that source the
order is file order. Rent the Runway uses the review date. The data card
says so. A user's last review is the test row when they have at least three
reviews. The one before that is validation, and is used only to calibrate.
"""

from __future__ import annotations

import pandas as pd


def assign_split(frame: pd.DataFrame) -> pd.Series:
    ordered = frame.sort_values(["user_id", "review_date", "row_id"], kind="mergesort")
    position = ordered.groupby("user_id", sort=False).cumcount()
    counts = ordered.groupby("user_id", sort=False)["row_id"].transform("size")
    split = pd.Series("train", index=ordered.index)
    multi = counts >= 3
    split[multi & (position == counts - 1)] = "test"
    split[multi & (position == counts - 2)] = "val"
    single = ~multi
    # Stable bucket so a one- or two-review shopper still lands in one split.
    bucket = pd.util.hash_pandas_object(ordered["user_id"], index=False) % 10
    split[single & (bucket == 0)] = "test"
    split[single & (bucket == 1)] = "val"
    return split.reindex(frame.index)
