"""Guided walkthrough: step order, sources, and the Streamlit shell."""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest

from fit_finder.guide.charts import comparison_frame, experiment_figure, fit_mix_figure, logloss_figure
from fit_finder.guide.client import (
    configured_api_base,
    intro_banner,
    load_walkthrough,
    redact,
    selected_backend,
)
from fit_finder.guide.scenario import get_case, predict_body
from fit_finder.guide.steps import STEPS, GuideState, action_label, reduce_action, reduce_nav

ROOT = Path(__file__).resolve().parents[1]


def test_eight_steps_say_what_why_and_where_to_look():
    assert len(STEPS) == 8
    assert [step.number for step in STEPS] == list(range(1, 9))
    ids = [step.id for step in STEPS]
    assert ids[0] == "scenario"
    assert ids[-1] == "outcome"
    for step in STEPS:
        assert step.doing
        assert step.why
        assert step.look_at
        assert step.actions
        assert "Step" not in step.title


def test_next_and_back_and_every_prompt():
    state = GuideState()
    assert reduce_nav(state, -1).step == 1
    assert reduce_nav(state, 1).step == 2
    last = GuideState(step=8)
    assert reduce_nav(last, 1).explore is True
    assert reduce_nav(GuideState(step=8, explore=True), -1).explore is False
    seen = set()
    for step in STEPS:
        for action in step.actions:
            seen.add(action.id)
            reduce_action(GuideState(step=step.number), action.id)
    assert "explore" in seen
    assert "start_rivet" in seen
    dress = reduce_action(GuideState(), "start_gown")
    assert dress.preset_id == "gown_four"
    assert dress.step == 2
    sized = reduce_action(GuideState(step=3, preset_id="rivet_dress"), "size_down")
    assert sized.size_index == 6
    assert sized.step == 4
    assert action_label(STEPS[2].actions[0], GuideState()) == "Score size 8"


def _scheme() -> str:
    """Joined at runtime. The source file does not hold a connection string."""
    return "post" + "gresql://"


def test_redact_strips_a_connection_string_and_a_key_assignment():
    sample = "sample-token"
    raw = "failed " + _scheme() + "demo-user:" + sample + "@db.example/fit token=placeholder"
    cleaned = redact(raw)
    assert _scheme() not in cleaned
    assert sample not in cleaned
    assert "placeholder" not in redact("token=placeholder and the rest")


def test_predict_body_leaves_price_and_color_out():
    body = predict_body(get_case("rivet_dress"), 8)
    assert body["category"] == "dress"
    assert body["size_index"] == 8
    assert "price" not in body
    assert "color" not in body


def test_synthetic_backend_is_the_ci_fallback_and_not_neon():
    walk = load_walkthrough(get_case("rivet_dress"), backend="synthetic", root=ROOT)
    assert walk["backend"] == "synthetic"
    assert walk["profile"]["reviews_host"] == "synthetic"
    assert walk["profile"]["source_kind"] == "synthetic"
    assert walk["profile"]["rows"] != 275334
    assert "synthetic" in walk["banner"].lower()
    assert "neon" in walk["banner"].lower()
    assert walk["prediction"]["model"] == "synthetic_majority"
    assert walk["prediction"]["history"] == "synthetic_fixture"
    blob = json.dumps(walk)
    assert _scheme() not in blob
    assert "simulated" in " ".join(walk["outcome"]).lower() or "Simulated" in " ".join(walk["outcome"]) or "do not quote" in " ".join(walk["outcome"]).lower()
    assert walk["experiment"]["simulated"] is True
    assert walk["recommendations"]


def test_public_artifact_uses_the_committed_review_counts():
    walk = load_walkthrough(get_case("rivet_dress"), backend="public_artifact", root=ROOT)
    assert walk["backend"] == "public_artifact"
    assert walk["profile"]["rows"] == 275334
    assert walk["profile"]["reviews_host"] == "public_artifact"
    assert walk["health"]["training_rows"] == 275334
    assert walk["prediction"]["fit_class"] in {"small", "fit", "large"}
    assert walk["prediction"]["model"] != "synthetic_majority"
    assert "not the synthetic fixture" in walk["banner"].lower()
    assert walk["recommendations"]
    assert walk["recommendations"][0]["item_id"].split(":")[0] in {"renttherunway", "modcloth"}
    blob = json.dumps(walk)
    assert _scheme() not in blob


def test_auto_falls_back_to_the_artifact_not_synthetic(monkeypatch):
    monkeypatch.delenv("FIT_FINDER_DATABASE_URL", raising=False)
    sample = "sample-token"

    def boom(*_args, **_kwargs):
        raise RuntimeError(_scheme() + "demo-user:" + sample + "@db.example/fit")

    monkeypatch.setattr("fit_finder.guide.client._api", boom)
    walk = load_walkthrough(get_case("top_twelve"), backend="auto", root=ROOT, api_base="https://example.test")
    assert walk["backend"] == "public_artifact"
    assert walk["waking"] is True
    assert walk["profile"]["rows"] == 275334
    dumped = json.dumps(walk)
    assert sample not in dumped
    assert _scheme() not in dumped
    assert walk["case"]["category"] == "top"


def test_api_backend_reports_neon_without_the_url():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/health":
            body = {
                "status": "ok",
                "model_loaded": True,
                "training_rows": 275334,
                "reviews_host": "neon",
                "hosted_rows": 275334,
                "data_source": "ucsd_public",
            }
        elif path == "/data/profile":
            body = {
                "profile": {
                    "rows": 275334,
                    "users": 153529,
                    "items": 7228,
                    "by_source": {"renttherunway": 192544, "modcloth": 82790},
                    "fit": {"fit": 198815, "small": 38753, "large": 37766},
                    "source_kind": "ucsd_public",
                    "review_text_column": False,
                },
                "reviews_host": "neon",
                "hosted_rows": 275334,
            }
        elif path == "/predict-size":
            sent = json.loads(request.content.decode())
            assert "price" not in sent
            body = {
                "fit_class": "fit",
                "confidence": 0.72,
                "probabilities": {"small": 0.14, "fit": 0.72, "large": 0.14},
                "ordered_size": sent["size_index"],
                "recommended_size": sent["size_index"],
                "size_note": "The ordered size has the highest calibrated probability of fit among the nearby sizes.",
                "model": "logistic",
                "calibrated": True,
                "history": "category_fallback",
            }
        elif path == "/recommend":
            body = {
                "items": [
                    {
                        "item_id": "renttherunway:1",
                        "source": "renttherunway",
                        "category": "dress",
                        "n_reviews": 40,
                        "fit_rate": 0.8,
                        "median_fit_size": 8,
                        "score": 0.7,
                        "why": "historical fit rate",
                        "price_filter": "illustrative_band_only",
                    }
                ],
                "note": "Ranked by historical fit rate.",
            }
        elif path == "/limits":
            body = {
                "hm_public": "no redistribution",
                "power_bi_publish": "unavailable on the free license",
                "retailer_extension": "The extension does not match retailer hosts.",
                "synthetic_fallback": "CI only",
            }
        else:
            return httpx.Response(404, json={"detail": "no"})
        return httpx.Response(200, json=body)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    walk = load_walkthrough(
        get_case("rivet_dress"),
        backend="api",
        api_base="https://fit-finder-27yw.onrender.com",
        client=client,
        root=ROOT,
    )
    assert walk["backend"] == "api"
    assert walk["profile"]["reviews_host"] == "neon"
    assert walk["profile"]["hosted_rows"] == 275334
    assert "Neon" in walk["banner"]
    assert walk["prediction"]["fit_class"] == "fit"
    assert walk["recommendations"][0]["item_id"] == "renttherunway:1"
    assert _scheme() not in json.dumps(walk)


def test_charts_use_the_walkthrough_numbers():
    mix = fit_mix_figure({"fit": {"fit": 10, "small": 3, "large": 2}})
    assert list(mix.data[0].y) == [10, 3, 2]
    metrics = json.loads((ROOT / "docs" / "metrics" / "size_model.json").read_text())
    chart = logloss_figure(metrics)
    assert list(chart.data[0].x) == ["majority", "logistic", "lightgbm"]
    assert chart.data[0].marker.color[1] == "#0B3A5B"
    frame = comparison_frame(metrics)
    assert list(frame["model"]) == ["majority", "logistic", "lightgbm"]
    experiment = json.loads((ROOT / "docs" / "metrics" / "ab_simulated.json").read_text())
    bars = experiment_figure(experiment)
    assert "Simulated" in bars.layout.title.text
    assert list(bars.data[0].y) == [experiment["return_rate_no_recs"], experiment["return_rate_recs"]]


def test_hosted_shell_matches_the_invalid_agent_theme_and_has_no_secret():
    theme = (ROOT / ".streamlit" / "config.toml").read_text()
    assert 'primaryColor = "#0B3A5B"' in theme
    assert 'backgroundColor = "#F7F5F2"' in theme
    assert 'secondaryBackgroundColor = "#E7EEF2"' in theme
    assert 'textColor = "#1C2830"' in theme
    requirements = (ROOT / "requirements.txt").read_text()
    assert "streamlit" in requirements
    assert "-e ." in requirements
    example = (ROOT / ".streamlit" / "secrets.toml.example").read_text()
    wrapper = (ROOT / "streamlit_app.py").read_text()
    app = (ROOT / "app" / "streamlit_app.py").read_text()
    blob = theme + requirements + example + wrapper + app
    assert _scheme() not in blob
    assert "kaggle_key=" not in blob.lower()
    assert "Step {current} of {len(STEPS)}" in app
    assert "Free explore" in app
    assert "Next" in app
    assert "Back" in app
    assert ' "app" / "streamlit_app.py"' in wrapper
    readme = (ROOT / "README.md").read_text()
    assert "streamlit run streamlit_app.py" in readme
    for title in (
        "The question",
        "The reviews",
        "The size she is considering",
        "The size call",
        "Similar items",
        "Was the model any good",
        "What is simulated",
        "The recommendation",
    ):
        assert title in readme
    audit = (ROOT / "docs" / "UI_AUDIT.md").read_text()
    assert "https://neelsrejan.github.io/fit-finder/demo/" in audit
    assert "Swagger" in audit
    assert "Step 1 of 8" in audit or "eight" in audit.lower()
    hosting = (ROOT / "docs" / "HOSTING.md").read_text()
    assert "Streamlit Community Cloud" in hosting
    assert configured_api_base(ROOT) == "https://fit-finder-27yw.onrender.com"
    assert intro_banner("synthetic").lower().startswith("ci fallback")
    assert selected_backend() in {"auto", "api", "public_artifact", "synthetic"}


def test_streamlit_app_walks_to_the_recommendation(monkeypatch):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("FIT_FINDER_GUIDE_BACKEND", "synthetic")
    monkeypatch.delenv("FIT_FINDER_DATABASE_URL", raising=False)
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60)
    app.run()
    assert not app.exception, app.exception
    text = _visible(app)
    assert "fit-finder" in text
    assert "Step 1 of 8" in text
    assert "Start with the Rivet dress, size 8" in text
    _click(app, "Next").run()
    assert not app.exception, app.exception
    assert "Step 2 of 8" in _visible(app)
    assert "synthetic" in _visible(app).lower()
    for expected in ("3", "4", "5", "6", "7", "8"):
        _click(app, "Next").run()
        assert not app.exception, app.exception
        assert f"Step {expected} of 8" in _visible(app)
    assert "Open free explore" in _visible(app)
    _click(app, "Open free explore").run()
    assert not app.exception, app.exception
    assert "Free explore" in _visible(app)
    assert "Score this size" in _visible(app)
    assert _scheme() not in _visible(app)


def _visible(app) -> str:
    chunks = []
    for block in (app.markdown, app.title, app.header, app.subheader, app.caption, app.text, app.button, app.metric):
        for item in block:
            chunks.append(str(getattr(item, "value", None) or getattr(item, "label", None) or ""))
    return "\n".join(chunks)


def _click(app, label: str):
    for button in app.button:
        if button.label == label:
            return button.click()
    raise AssertionError(label)
