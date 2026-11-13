"""Item-item collaborative filtering on purchase counts.

The score for a candidate item is the cosine similarity of its buyer vector
to the items the shopper already bought, averaged over those items. Buyers
are the training transactions only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _matrix(transactions: pd.DataFrame) -> tuple[np.ndarray, list[str], list[str]]:
    users = sorted(transactions["user_id"].unique())
    items = sorted(transactions["item_id"].unique())
    user_index = {user: i for i, user in enumerate(users)}
    item_index = {item: i for i, item in enumerate(items)}
    matrix = np.zeros((len(users), len(items)), dtype=np.float64)
    for row in transactions.itertuples(index=False):
        matrix[user_index[row.user_id], item_index[row.item_id]] = 1.0
    return matrix, users, items


def cosine_item_item(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=0)
    norms[norms == 0] = 1.0
    normal = matrix / norms
    return normal.T @ normal


def rank_for_user(
    owned: list[str],
    similarity: np.ndarray,
    items: list[str],
    limit: int,
) -> list[str]:
    index = {item: i for i, item in enumerate(items)}
    scores = np.zeros(len(items))
    used = [index[item] for item in owned if item in index]
    if not used:
        return []
    for item_i in used:
        scores += similarity[item_i]
    for item_i in used:
        scores[item_i] = -np.inf
    order = np.argsort(-scores)
    ranked = []
    for position in order:
        if scores[position] == -np.inf:
            continue
        ranked.append(items[int(position)])
        if len(ranked) >= limit:
            break
    return ranked


def leave_one_out_hit_rate(transactions: pd.DataFrame, k: int = 10) -> dict:
    """Hold out each user's last row. Rank the rest of the catalog."""
    ordered = transactions.sort_values(["user_id", "date", "item_id"])
    last = ordered.groupby("user_id", as_index=False).tail(1)
    train = ordered.drop(index=last.index)
    matrix, _users, items = _matrix(train)
    similarity = cosine_item_item(matrix)
    owned = train.groupby("user_id")["item_id"].apply(list).to_dict()
    hits = []
    reciprocal = []
    for row in last.itertuples(index=False):
        history = owned.get(row.user_id, [])
        ranked = rank_for_user(history, similarity, items, limit=max(k, len(items)))
        if row.item_id in ranked[:k]:
            hits.append(1.0)
        else:
            hits.append(0.0)
        if row.item_id in ranked:
            reciprocal.append(1.0 / (ranked.index(row.item_id) + 1))
        else:
            reciprocal.append(0.0)
    n = len(hits)
    return {
        "hit_rate": float(np.mean(hits)) if n else 0.0,
        "mrr": float(np.mean(reciprocal)) if n else 0.0,
        "n": n,
        "k": k,
        "method": "item_item_cosine",
        "simulated_fixture": True,
    }
