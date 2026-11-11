"""FastAPI app. Model and catalog are loaded at startup when the files exist."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from fit_finder.api.schemas import (
    EventRequest,
    EventResponse,
    RecommendItem,
    RecommendRequest,
    RecommendResponse,
    SizeRequest,
    SizeResponse,
)
from fit_finder.config import load_settings
from fit_finder.events.log import append_event
from fit_finder.model.predict import load_bundle, predict_one
from fit_finder.recommend.rank import rank_items

app = FastAPI(
    title="fit-finder",
    version="0.1.0",
    description=(
        "Local size and fit API for a portfolio demo. "
        "Confidence comes from a model calibrated on public fit reviews. "
        "Events posted here are requests to this process, not store traffic."
    ),
)

_state: dict = {"bundle": None, "catalog": None, "settings": None}


@app.on_event("startup")
def _load() -> None:
    settings = load_settings()
    _state["settings"] = settings
    if settings.model_path.exists():
        _state["bundle"] = load_bundle(settings.model_path)
    if settings.catalog_path.exists():
        import pandas as pd

        _state["catalog"] = pd.read_parquet(settings.catalog_path)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": _state["bundle"] is not None,
        "catalog_loaded": _state["catalog"] is not None,
        "hm": "blocked_pending_kaggle_key",
        "power_bi_publish": "blocked_pending_microsoft_account",
    }


@app.post("/predict-size", response_model=SizeResponse)
def predict_size(body: SizeRequest) -> SizeResponse:
    bundle = _state["bundle"]
    if bundle is None:
        raise HTTPException(status_code=503, detail="size model file is not loaded")
    result = predict_one(bundle, body.model_dump())
    return SizeResponse(**result)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(body: RecommendRequest) -> RecommendResponse:
    catalog = _state["catalog"]
    if catalog is None:
        raise HTTPException(status_code=503, detail="item catalog is not loaded")
    ranked = rank_items(
        catalog,
        category=body.category,
        size_index=body.size_index,
        limit=body.limit,
        exclude_item_id=body.exclude_item_id,
        price=body.price,
        color=body.color,
    )
    items = []
    for row in ranked.to_dict(orient="records"):
        row["n_reviews"] = int(row["n_reviews"])
        row["fit_rate"] = float(row["fit_rate"])
        row["median_fit_size"] = float(row["median_fit_size"])
        row["score"] = float(row["score"])
        items.append(RecommendItem(**row))
    return RecommendResponse(
        items=items,
        note="Ranked by historical fit rate and size closeness. Price bands are illustrative. UCSD items have no color.",
    )


@app.post("/events", response_model=EventResponse)
def post_event(body: EventRequest) -> EventResponse:
    settings = _state["settings"] or load_settings()
    event_id = append_event(settings.events_path, body.model_dump())
    return EventResponse(accepted=True, event_id=event_id, simulated=False)


def main() -> None:
    import uvicorn

    uvicorn.run("fit_finder.api.app:app", host="127.0.0.1", port=8000, reload=False)
