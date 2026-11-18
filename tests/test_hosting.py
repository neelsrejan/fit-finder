"""Hosted path: public UCSD artifact, no secrets, fixture refused."""

from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from fit_finder.data.download import ATTEMPTS, BACKOFF_SECONDS, SOURCES, PublicDownloadError, download
from fit_finder.data.pipeline import PROVENANCE_NOTE, _profile, write_profile
from fit_finder.data.synthetic import make_reviews
from fit_finder.hm.adapter import public_hosting_block_reason
from fit_finder.store import HostedStoreError, assert_public_frame, require_database_url

ROOT = Path(__file__).resolve().parents[1]


def test_public_download_urls_need_no_token():
    assert SOURCES["modcloth"].startswith("https://mcauleylab.ucsd.edu/")
    assert SOURCES["renttherunway"].startswith("https://mcauleylab.ucsd.edu/")
    assert "kaggle" not in " ".join(SOURCES.values())


def test_missing_database_url_names_the_variable(monkeypatch):
    monkeypatch.delenv("FIT_FINDER_DATABASE_URL", raising=False)
    try:
        require_database_url()
    except HostedStoreError as exc:
        text = str(exc)
    else:
        raise AssertionError("expected HostedStoreError")
    assert "FIT_FINDER_DATABASE_URL" in text
    assert "neon.com" in text
    assert "postgresql://" not in text
    assert "password" not in text.lower()


def test_synthetic_fixture_is_not_a_hosted_load():
    frame = make_reviews(n_users=20, reviews_each=4, seed=1)
    try:
        assert_public_frame(frame)
    except HostedStoreError as exc:
        assert "synthetic" in str(exc).lower() or "Refusing" in str(exc)
    else:
        raise AssertionError("fixture must not pass the public-table check")


def test_hm_public_block_does_not_embed_a_key():
    text = public_hosting_block_reason()
    assert "redistribution" in text
    assert "KAGGLE_KEY" in text
    assert not re.search(r"kaggle_key\s*=\s*\S+", text, re.IGNORECASE)


def test_public_config_files_agree_and_hold_no_secret():
    public = json.loads((ROOT / "deploy" / "public.json").read_text())
    config = (ROOT / "extension" / "config.js").read_text()
    match = re.search(r'FIT_FINDER_API_BASE = "([^"]*)"', config)
    assert match is not None
    assert match.group(1) == public["apiBase"]
    blob = json.dumps(public) + config
    assert "postgresql://" not in blob
    assert "kaggle" not in blob.lower()


def test_committed_artifact_serves_the_public_catalog(monkeypatch, tmp_path):
    monkeypatch.delenv("FIT_FINDER_DATABASE_URL", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("FIT_FINDER_MODEL", str(ROOT / "models" / "size_model.joblib"))
    monkeypatch.setenv("FIT_FINDER_CATALOG", str(ROOT / "models" / "catalog.parquet"))
    monkeypatch.setenv("FIT_FINDER_EVENTS", str(tmp_path / "events.jsonl"))
    monkeypatch.setenv("FIT_FINDER_PROVENANCE", str(ROOT / "models" / "provenance.json"))
    monkeypatch.setenv("FIT_FINDER_PROFILE", str(ROOT / "docs" / "metrics" / "data_profile.json"))
    from fit_finder.api.app import _load, app

    _load()
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    body = health.json()
    assert body["model_loaded"] is True
    assert body["training_rows"] == 275334
    assert body["data_source"] == "ucsd_public"
    assert body["reviews_host"] == "not_configured"
    assert body["hm_public"] == "blocked_license_noncommercial_no_redistribution"
    assert body["power_bi_publish"] == "unavailable_on_free_license"
    dumped = json.dumps(body)
    assert "postgresql://" not in dumped
    assert "super-secret" not in dumped
    items = client.get("/items", params={"category": "dress", "limit": 2})
    assert items.status_code == 200
    rows = items.json()["items"]
    assert len(rows) == 2
    assert rows[0]["n_reviews"] > 10
    assert rows[0]["item_id"].split(":")[0] in {"renttherunway", "modcloth"}
    scored = client.post("/predict-size", json={"category": "dress", "size_index": 8, "height_in": 65})
    assert scored.status_code == 200
    assert scored.json()["fit_class"] in {"small", "fit", "large"}
    profile = client.get("/data/profile")
    assert profile.status_code == 200
    assert profile.json()["profile"]["rows"] == 275334


def test_download_retries_ssl_eof_then_keeps_the_body(tmp_path, monkeypatch):
    calls = {"n": 0}
    sleeps: list[float] = []

    class Body:
        def __init__(self) -> None:
            self._pending = b"not-empty"

        def read(self, _size: int) -> bytes:
            payload, self._pending = self._pending, b""
            return payload

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> bool:
            return False

    def fake_urlopen(_request, timeout=0):
        assert timeout == 60
        calls["n"] += 1
        if calls["n"] < 2:
            raise OSError("EOF occurred in violation of protocol (_ssl.c:2427)")
        return Body()

    monkeypatch.setattr("fit_finder.data.download.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("fit_finder.data.download.time.sleep", lambda seconds: sleeps.append(seconds))
    path = download(tmp_path, "modcloth", force=True)
    assert path.read_bytes() == b"not-empty"
    assert calls["n"] == 2
    assert sleeps == [BACKOFF_SECONDS[0]]
    assert list(tmp_path.glob("*.part")) == []


def test_download_stops_on_a_missing_file_without_backoff(tmp_path, monkeypatch):
    import urllib.error

    sleeps: list[float] = []

    def fake_urlopen(request, timeout=0):
        raise urllib.error.HTTPError(request.full_url, 404, "missing", hdrs=None, fp=None)

    monkeypatch.setattr("fit_finder.data.download.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("fit_finder.data.download.time.sleep", lambda seconds: sleeps.append(seconds))
    try:
        download(tmp_path, "modcloth", force=True)
    except PublicDownloadError as exc:
        assert "404" in str(exc)
    else:
        raise AssertionError("a 404 must fail")
    assert sleeps == []
    assert ATTEMPTS == 4


def test_profile_null_shares_stay_at_four_decimals_and_provenance_keeps_its_sentence(tmp_path):
    frame = make_reviews(n_users=8, reviews_each=4, seed=1)
    frame.loc[frame.index[:3], "height_in"] = float("nan")
    first = _profile(frame)
    second = _profile(frame)
    assert first == second
    for share in first["null_share"].values():
        assert share == round(share, 4)
    write_profile(tmp_path, first)
    note = (tmp_path / "models" / "provenance.json").read_text()
    assert "Re-running fit-finder-pipeline rewrites this file from the download." in note
    assert PROVENANCE_NOTE in note


def test_demo_page_calls_the_api_from_config():
    html = (ROOT / "demo-store" / "index.html").read_text()
    script = (ROOT / "demo-store" / "panel.js").read_text()
    assert "panel.js" in html
    assert "config.json" in script
    assert "127.0.0.1:8000" in script
    for banned in ("amazon", "nordstrom", "nike.com", "hm.com"):
        assert banned not in script
