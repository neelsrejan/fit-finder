"""Synthetic reviews that match the cleaned schema.

Used by tests and by the committed fixture. These rows are not the UCSD
files. The model card numbers come from the UCSD training run.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fit_finder.data.schema import REVIEW_COLUMNS


def make_reviews(n_users: int = 40, reviews_each: int = 4, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    categories = np.array(["dress", "top", "jeans", "skirt"])
    bodies = np.array(["hourglass", "athletic", "straight", "pear"])
    rows = []
    row_id = 0
    for user in range(n_users):
        true_size = int(rng.integers(6, 14))
        height = float(rng.normal(65, 3))
        weight = float(rng.normal(145, 20))
        for step in range(reviews_each):
            category = str(categories[(user + step) % len(categories)])
            ordered = true_size + int(rng.choice([-1, 0, 0, 1]))
            if ordered < true_size:
                fit = "small"
            elif ordered > true_size:
                fit = "large"
            else:
                fit = "fit"
            source = "renttherunway" if user % 2 == 0 else "modcloth"
            rows.append(
                {
                    "source": source,
                    "user_id": f"{source}:u{user}",
                    "item_id": f"{source}:item-{(user + step) % 12}",
                    "category": category,
                    "size_raw": str(ordered),
                    "size_index": float(ordered),
                    "fit": fit,
                    "rating": float(rng.integers(6, 11)),
                    "height_in": height,
                    "weight_lbs": weight if source == "renttherunway" else np.nan,
                    "bust_band": 34.0,
                    "cup": "c",
                    "age": 30.0 if source == "renttherunway" else np.nan,
                    "body_type": str(bodies[user % len(bodies)]),
                    "rented_for": "work" if source == "renttherunway" else "unknown",
                    "review_date": pd.Timestamp("2020-01-01") + pd.Timedelta(days=user * 10 + step),
                    "row_id": row_id,
                }
            )
            row_id += 1
    return pd.DataFrame(rows, columns=list(REVIEW_COLUMNS))
