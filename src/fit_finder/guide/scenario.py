"""The shopper the walkthrough follows.

Prices, colors, and the item ids are fixtures, the same contract as the
demo page. The score still comes from public fit reviews when the backend
is the API or the committed artifact.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShopperCase:
    id: str
    label: str
    title: str
    story: str
    category: str
    size_index: float
    height_in: float
    weight_lbs: float | None
    age: float | None
    price: float
    color: str
    item_id: str


CASES: tuple[ShopperCase, ...] = (
    ShopperCase(
        id="rivet_dress",
        label="Rivet dress, size 8",
        title="Rivet dress",
        story=(
            "A shopper is on the demo page, looking at a sleeveless dress. "
            "The page says size 8, $128, black. She is 5 ft 5 in and new here, "
            "so there is no personal fit history. The dress, the price, and the "
            "colors are fixtures. The score, when the live path is on, comes from "
            "public fit reviews."
        ),
        category="dress",
        size_index=8,
        height_in=65,
        weight_lbs=140,
        age=32,
        price=128,
        color="black",
        item_id="demo-dress-1",
    ),
    ShopperCase(
        id="gown_four",
        label="Gown, size 4",
        title="Gown",
        story=(
            "Same question, different garment. She is considering a gown in size 4 "
            "and she is 5 ft 8 in. Gown is one of the larger held-out categories. "
            "The price and the navy color are fixtures."
        ),
        category="gown",
        size_index=4,
        height_in=68,
        weight_lbs=135,
        age=29,
        price=220,
        color="navy",
        item_id="demo-gown-1",
    ),
    ShopperCase(
        id="top_twelve",
        label="Top, size 12",
        title="Top",
        story=(
            "She is considering a top in size 12. She is 5 ft 2 in. "
            "The ranker stays inside this category. The price is a fixture."
        ),
        category="top",
        size_index=12,
        height_in=62,
        weight_lbs=150,
        age=41,
        price=48,
        color="red",
        item_id="demo-top-1",
    ),
)

_BY_ID = {case.id: case for case in CASES}


def get_case(case_id: str) -> ShopperCase:
    try:
        return _BY_ID[case_id]
    except KeyError as exc:
        known = ", ".join(_BY_ID)
        raise KeyError(f"unknown case {case_id!r}; expected one of {known}") from exc


def active_size(case: ShopperCase, override: float | None) -> float:
    if override is None:
        return float(case.size_index)
    return float(override)


def predict_body(case: ShopperCase, size: float) -> dict:
    """Body for `/predict-size`. Price and color are not model inputs."""
    body: dict = {
        "category": case.category,
        "size_index": float(size),
        "source": "demo-store",
        "item_id": case.item_id,
        "height_in": float(case.height_in),
    }
    if case.weight_lbs is not None:
        body["weight_lbs"] = float(case.weight_lbs)
    if case.age is not None:
        body["age"] = float(case.age)
    return body


def recommend_body(case: ShopperCase, size: float, recommended_size: float | None) -> dict:
    target = float(size if recommended_size is None else recommended_size)
    return {
        "category": case.category,
        "size_index": target,
        "limit": 5,
        "exclude_item_id": case.item_id,
        "price": float(case.price),
        "color": case.color,
    }


def history_plain(code: str) -> str:
    if code == "item":
        return "This item has public reviews, so the call uses that item's history."
    if code == "category_fallback":
        return (
            "This page's item id is not in the public catalog. "
            "The call uses the category's usual fit size. She has no personal history."
        )
    if code == "synthetic_fixture":
        return "This score uses the synthetic fixture only. It is the CI fallback."
    return "History for this call is not item-level."
