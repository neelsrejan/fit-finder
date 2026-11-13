"""Tests for parsing, the model loop, the API, and the blocked H&M path."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from fit_finder.config import load_settings
from fit_finder.data.clean import parse_bust, parse_fit, parse_height, parse_weight, record_from_modcloth, record_from_renttherunway
from fit_finder.data.synthetic import make_reviews
from fit_finder.events.ab import simulate, summarize
from fit_finder.events.power import sample_size_per_arm, z_value
from fit_finder.hm.adapter import HMDownloadBlocked, download_kaggle
from fit_finder.hm.compare import compare
from fit_finder.model.predict import predict_one
from fit_finder.model.split import assign_split
from fit_finder.model.train import bundle_from_result, direction_hit, public_metrics, save_bundle, train_models
from fit_finder.pageparse import parse_product_html
from fit_finder.recommend.catalog import build_catalog
from fit_finder.recommend.rank import rank_items

ROOT = Path(__file__).resolve().parents[1]


def test_height_weight_bust_parsers():
    assert parse_height("5' 8\"") == 68
    assert parse_height("5ft 6in") == 66
    assert parse_height("nope") is None
    assert parse_weight("137lbs") == 137
    assert parse_bust("34d") == (34.0, "d")
    assert parse_fit("Large") == "large"
    assert parse_fit("tiny") is None


def test_records_drop_review_text_and_names():
    rtr = record_from_renttherunway(
        {
            "fit": "fit",
            "user_id": "1",
            "item_id": "9",
            "size": 8,
            "height": "5' 4\"",
            "weight": "120lbs",
            "bust size": "32b",
            "category": "Dress",
            "body type": "Athletic",
            "rented for": "Party",
            "review_text": "secret story",
            "user_name": "Ada",
            "rating": "10",
            "age": "28",
            "review_date": "April 20, 2016",
        },
        0,
    )
    assert rtr is not None
    assert "secret story" not in json.dumps(rtr)
    assert rtr["user_id"] == "renttherunway:1"
    assert rtr["category"] == "dress"
    assert rtr["height_in"] == 64
    mod = record_from_modcloth(
        {
            "item_id": "5",
            "user_id": "9",
            "size": 7,
            "fit": "small",
            "category": "new",
            "bra size": "34",
            "cup size": "d",
            "height": "5ft 6in",
            "user_name": "Emily",
            "quality": 5,
            "length": "just right",
        },
        3,
    )
    assert mod is not None
    assert "Emily" not in json.dumps(mod)
    assert "length" not in mod
    assert mod["bust_band"] == 34


def test_split_holds_out_the_latest_review():
    frame = make_reviews(n_users=10, reviews_each=4, seed=1)
    frame = frame.copy()
    frame["split"] = assign_split(frame)
    one = frame[frame["user_id"].eq(frame["user_id"].iloc[0])]
    latest = one.sort_values("review_date").iloc[-1]
    assert latest["split"] == "test"
    assert set(frame["split"]) <= {"train", "val", "test"}


def test_direction_rules():
    assert direction_hit("fit", 8, 8)
    assert not direction_hit("fit", 8, 10)
    assert direction_hit("small", 8, 10)
    assert direction_hit("large", 8, 6)


def test_train_on_synthetic_rows_and_score(tmp_path):
    frame = make_reviews(n_users=36, reviews_each=4, seed=3)
    result = train_models(frame, lightgbm_rounds=15)
    metrics = public_metrics(result)
    for name in ("majority", "logistic", "lightgbm"):
        assert 0.0 <= metrics["test"][name]["accuracy"] <= 1.0
        assert metrics["test"][name]["log_loss"] > 0
    bundle = bundle_from_result(result)
    path = tmp_path / "model.joblib"
    save_bundle(bundle, path)
    from fit_finder.model.predict import load_bundle

    loaded = load_bundle(path)
    scored = predict_one(
        loaded,
        {"category": "dress", "size_index": 8, "height_in": 65, "body_type": "athletic", "source": "renttherunway"},
    )
    assert scored["fit_class"] in {"small", "fit", "large"}
    assert abs(sum(scored["probabilities"].values()) - 1) < 1e-6
    assert scored["recommended_size"] == pytest.approx(scored["recommended_size"])


def test_ranker_stays_in_category():
    frame = make_reviews(n_users=20, reviews_each=4, seed=2)
    catalog = build_catalog(frame)
    ranked = rank_items(catalog, category="dress", size_index=8, limit=3)
    assert len(ranked) <= 3
    assert set(ranked["category"]) == {"dress"}
    assert ranked["score"].is_monotonic_decreasing


def test_simulated_ab_is_labeled_and_reproducible():
    first = summarize(simulate())
    second = summarize(simulate())
    assert first == second
    assert first["simulated"] is True
    assert first["sample_size_per_arm_for_2pp"] > 100
    assert abs(z_value(0.975) - 1.96) < 0.01
    assert sample_size_per_arm(0.30, 0.28) > 0


def test_hm_download_is_blocked(tmp_path, monkeypatch):
    monkeypatch.delenv("FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    with pytest.raises(HMDownloadBlocked):
        download_kaggle(tmp_path)
    report = compare()
    assert report["content"]["simulated_fixture"] is True
    assert "not downloaded" in report["blocked"]


def test_manifest_does_not_target_retailers():
    manifest = json.loads((ROOT / "extension" / "manifest.json").read_text())
    blob = json.dumps(manifest).lower()
    for banned in ["amazon", "nordstrom", "nike.com", "renttherunway.com", "modcloth.com", "hm.com"]:
        assert banned not in blob
    matches = " ".join(manifest["content_scripts"][0]["matches"])
    assert "localhost" in matches
    assert "127.0.0.1" in matches


def test_demo_page_parser():
    html = (ROOT / "demo-store" / "index.html").read_text()
    product = parse_product_html(html)
    assert product["product_id"] == "demo-dress-1"
    assert product["category"] == "dress"
    assert product["price"] == "128"
    assert "navy" in product["colors"]
    assert product["selected_size"] == "8"
    assert any(row["size"] == "8" for row in product["sizes"])


def test_api_round_trip(tmp_path, monkeypatch):
    frame = make_reviews(n_users=36, reviews_each=4, seed=5)
    result = train_models(frame, lightgbm_rounds=10)
    model_path = tmp_path / "model.joblib"
    save_bundle(bundle_from_result(result), model_path)
    catalog_path = tmp_path / "catalog.parquet"
    build_catalog(frame).to_parquet(catalog_path, index=False)
    monkeypatch.setenv("FIT_FINDER_MODEL", str(model_path))
    monkeypatch.setenv("FIT_FINDER_CATALOG", str(catalog_path))
    monkeypatch.setenv("FIT_FINDER_EVENTS", str(tmp_path / "events.jsonl"))
    from fit_finder.api.app import _load, app

    _load()
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["model_loaded"] is True
    assert health.json()["hm"] == "blocked_pending_kaggle_key"
    scored = client.post("/predict-size", json={"category": "dress", "size_index": 8, "height_in": 65})
    assert scored.status_code == 200
    body = scored.json()
    assert body["probabilities"]["fit"] >= 0
    recs = client.post("/recommend", json={"category": "dress", "size_index": 8, "limit": 2})
    assert recs.status_code == 200
    assert len(recs.json()["items"]) <= 2
    posted = client.post(
        "/events",
        json={"event_type": "click", "session_id": "local-demo", "arm": "recs", "category": "dress"},
    )
    assert posted.status_code == 200
    assert posted.json()["simulated"] is False
    bad = client.post("/predict-size", json={"category": "dress"})
    assert bad.status_code == 422


def test_settings_repr_hides_kaggle_key(monkeypatch):
    monkeypatch.setenv("KAGGLE_KEY", "super-secret-token")
    monkeypatch.setenv("KAGGLE_USERNAME", "neel")
    text = repr(load_settings())
    assert "super-secret-token" not in text
    assert "kaggle_key=set" in text


def test_fixture_csv_matches_schema():
    frame = pd.read_csv(ROOT / "data" / "fixtures" / "reviews.csv")
    assert {"fit", "size_index", "user_id", "item_id", "category"} <= set(frame.columns)
    assert set(frame["fit"]) <= {"small", "fit", "large"}
    assert "review_text" not in frame.columns
