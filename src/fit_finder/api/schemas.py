"""Request and response bodies for the local API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SizeRequest(BaseModel):
    category: str = Field(examples=["dress"])
    size_index: float = Field(description="Numeric size the shopper is considering.")
    source: str = "unknown"
    item_id: str | None = None
    height_in: float | None = None
    weight_lbs: float | None = None
    age: float | None = None
    bust_band: float | None = None
    cup_index: float | None = None
    body_type: str | None = None
    rented_for: str | None = None
    user_n: float | None = None
    user_p_small: float | None = None
    user_p_large: float | None = None


class SizeResponse(BaseModel):
    fit_class: Literal["small", "fit", "large"]
    confidence: float
    probabilities: dict[str, float]
    ordered_size: float
    recommended_size: float
    size_note: str
    model: str
    calibrated: bool
    history: str


class RecommendRequest(BaseModel):
    category: str
    size_index: float
    limit: int = Field(default=5, ge=1, le=20)
    exclude_item_id: str | None = None
    price: float | None = Field(default=None, description="Optional. Compared with an illustrative category band, not an observed item price.")
    color: str | None = None


class RecommendItem(BaseModel):
    item_id: str
    source: str
    category: str
    n_reviews: int
    fit_rate: float
    median_fit_size: float
    score: float
    why: str
    price_filter: str


class RecommendResponse(BaseModel):
    items: list[RecommendItem]
    note: str


class EventRequest(BaseModel):
    event_type: Literal["impression", "click", "purchase", "return", "prediction"]
    session_id: str
    item_id: str | None = None
    category: str | None = None
    arm: Literal["recs", "no_recs", "unassigned"] = "unassigned"
    metadata: dict | None = None


class EventResponse(BaseModel):
    accepted: bool
    event_id: str
    simulated: bool
