"""FastAPI app. Model and catalog load at startup when the files exist.

The process binds to 0.0.0.0 only when PORT is set, which is what the free
host injects. A laptop run of fit-finder-api stays on 127.0.0.1.
"""

from __future__ import annotations

import json
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from fit_finder.api.schemas import (
    EventRequest,
    EventResponse,
    RecommendItem,
    RecommendRequest,
    RecommendResponse,
    SizeRequest,
    SizeResponse,
)
from fit_finder.config import PAGES_ORIGIN, load_settings
from fit_finder.events.log import append_event, read_events
from fit_finder.hm.adapter import public_hosting_block_reason
from fit_finder.model.predict import load_bundle, predict_one
from fit_finder.recommend.rank import rank_items
from fit_finder.store import HostedStoreError, append_hosted_event, read_hosted_events, review_stats

app = FastAPI(
    title="fit-finder",
    version="0.1.0",
    description=(
        "Size and fit API for a portfolio demo. "
        "Confidence comes from a model calibrated on the public UCSD fit reviews. "
        "Events posted here are requests to this process, not store traffic. "
        "Shopper-return figures in the Power BI extracts are simulated."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[PAGES_ORIGIN],
    allow_origin_regex=r"https://[\w.-]+\.onrender\.com|http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

_state: dict = {"bundle": None, "catalog": None, "settings": None}


def _read_json(path) -> dict | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text())


@app.on_event("startup")
def _load() -> None:
    settings = load_settings()
    _state["settings"] = settings
    if settings.model_path.exists():
        _state["bundle"] = load_bundle(settings.model_path)
    if settings.catalog_path.exists():
        import pandas as pd

        _state["catalog"] = pd.read_parquet(settings.catalog_path)


def _hosted_status() -> dict:
    settings = _state["settings"] or load_settings()
    if not settings.database_url:
        return {
            "reviews_host": "not_configured",
            "events_store": "ephemeral_file",
            "reviews_host_detail": (
                "FIT_FINDER_DATABASE_URL is not set. "
                "The model and catalog in this process were trained on the public UCSD reviews. "
                "The cleaned review table is not in Neon until that variable is set to the direct connection string."
            ),
        }
    try:
        stats = review_stats()
    except HostedStoreError as exc:
        return {
            "reviews_host": "configured_unreachable",
            "events_store": "hosted_postgres_unreachable",
            "reviews_host_detail": str(exc),
        }
    return {
        "reviews_host": "neon",
        "events_store": "hosted_postgres",
        "hosted_rows": stats["rows"],
        "hosted_meta": stats["meta"],
    }


@app.get("/health")
def health() -> dict:
    settings = _state["settings"] or load_settings()
    profile = _read_json(settings.profile_path) or {}
    provenance = _read_json(settings.provenance_path) or {}
    body = {
        "status": "ok",
        "model_loaded": _state["bundle"] is not None,
        "catalog_loaded": _state["catalog"] is not None,
        "data_source": provenance.get("source_kind") or profile.get("source_kind") or "ucsd_public_artifact",
        "training_rows": provenance.get("rows") or profile.get("rows"),
        "hm": "blocked_pending_kaggle_key",
        "hm_public": "blocked_license_noncommercial_no_redistribution",
        "power_bi_publish": "unavailable_on_free_license",
        "public_api_url_configured": bool(settings.public_api_url),
    }
    body.update(_hosted_status())
    return body


@app.get("/data/profile")
def data_profile() -> dict:
    """Committed public-data counts, plus live hosted counts when Neon is set."""
    settings = _state["settings"] or load_settings()
    profile = _read_json(settings.profile_path)
    if profile is None:
        raise HTTPException(status_code=503, detail="data profile file is not in this build")
    body = {"profile": profile, "provenance": _read_json(settings.provenance_path)}
    body.update(_hosted_status())
    if body["reviews_host"] == "neon":
        try:
            body["hosted"] = review_stats()
        except HostedStoreError as exc:
            body["hosted_error"] = str(exc)
    return body


@app.get("/items")
def items(
    category: str = Query(default="dress"),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Item aggregates from the public-review catalog. No shopper rows."""
    catalog = _state["catalog"]
    if catalog is None:
        raise HTTPException(status_code=503, detail="item catalog is not loaded")
    matched = catalog[catalog["category"].astype(str).str.lower().eq(category.strip().lower())]
    taken = matched.head(limit)
    rows = []
    for row in taken.to_dict(orient="records"):
        rows.append(
            {
                "item_id": str(row["item_id"]),
                "source": str(row["source"]),
                "category": str(row["category"]),
                "n_reviews": int(row["n_reviews"]),
                "fit_rate": float(row["fit_rate"]),
                "median_fit_size": float(row["median_fit_size"]),
            }
        )
    return {
        "category": category.strip().lower(),
        "items": rows,
        "note": "fit_rate is the share of public reviews whose label was fit. It is not a return rate.",
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
    found = []
    for row in ranked.to_dict(orient="records"):
        row["n_reviews"] = int(row["n_reviews"])
        row["fit_rate"] = float(row["fit_rate"])
        row["median_fit_size"] = float(row["median_fit_size"])
        row["score"] = float(row["score"])
        found.append(RecommendItem(**row))
    return RecommendResponse(
        items=found,
        note="Ranked by historical fit rate and size closeness. Price bands are illustrative. UCSD items have no color.",
    )


@app.post("/events", response_model=EventResponse)
def post_event(body: EventRequest) -> EventResponse:
    settings = _state["settings"] or load_settings()
    payload = body.model_dump()
    if settings.database_url:
        try:
            event_id = append_hosted_event(payload)
        except HostedStoreError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    else:
        event_id = append_event(settings.events_path, payload)
    return EventResponse(accepted=True, event_id=event_id, simulated=False)


@app.get("/events")
def list_events(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    settings = _state["settings"] or load_settings()
    if settings.database_url:
        try:
            rows = read_hosted_events(limit)
        except HostedStoreError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"store": "hosted_postgres", "events": rows, "simulated": False}
    return {
        "store": "ephemeral_file",
        "events": read_events(settings.events_path, limit),
        "simulated": False,
        "note": "This file is local to the process and is wiped when a free web instance sleeps. Set FIT_FINDER_DATABASE_URL for durable demo events.",
    }


@app.get("/limits")
def limits() -> dict:
    """What this public service will not do, in one response."""
    return {
        "hm_public": public_hosting_block_reason(),
        "power_bi_publish": (
            "A free Power BI license cannot create a Publish to web embed code, "
            "and Publish to web does not support report-level DAX measures. "
            "Pro is a paid license, so this project does not use it. "
            "The CSV extracts are the public artifact."
        ),
        "retailer_extension": "The extension does not match retailer hosts.",
        "synthetic_fallback": "The synthetic review fixture and the simulated shopper experiment stay available for CI and offline runs.",
    }


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    # Render and the container set PORT. A bare laptop command does not.
    host = os.environ.get("FIT_FINDER_BIND", "0.0.0.0" if "PORT" in os.environ else "127.0.0.1")
    uvicorn.run("fit_finder.api.app:app", host=host, port=port, reload=False)
