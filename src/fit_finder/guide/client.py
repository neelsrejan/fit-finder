"""One walkthrough payload.

`api` reads the Render service, which reads Neon. `public_artifact` uses the
committed model, catalog, and metric files from the public UCSD run.
`synthetic` is the CI fallback and says so. `auto` tries the API, then the
committed artifact. It does not fall through to synthetic rows.
"""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from fit_finder.config import resolve_root
from fit_finder.guide.scenario import (
    ShopperCase,
    active_size,
    history_plain,
    predict_body,
    recommend_body,
)

BACKENDS = ("auto", "api", "public_artifact", "synthetic")
_URL_RE = re.compile(r"postgres(?:ql)?://\S+|https?://\S*:[^@\s/]+@", re.IGNORECASE)
_SECRET_RE = re.compile(r"(api[_-]?key|password|secret|token)\s*[:=]\s*\S+", re.IGNORECASE)

EXTRACTS: tuple[dict[str, str], ...] = (
    {
        "file": "fact_model_score.csv",
        "kind": "held-out",
        "what": "Sample of held-out predictions from the public reviews. No shopper id and no measurements.",
    },
    {
        "file": "fact_shopper.csv",
        "kind": "simulated",
        "what": "Simulated shoppers for the recommendations-versus-none experiment.",
    },
    {
        "file": "fact_event.csv",
        "kind": "simulated",
        "what": "Simulated impressions, clicks, and returns.",
    },
    {
        "file": "dim_arm.csv",
        "kind": "simulated",
        "what": "The two experiment arms.",
    },
    {
        "file": "assumptions.csv",
        "kind": "simulated",
        "what": "Named probabilities and the assumed dollars per return.",
    },
    {
        "file": "summary.json",
        "kind": "simulated",
        "what": "The same simulated readout as the chart on this step.",
    },
)


class GuideSourceError(RuntimeError):
    """The requested source did not return a walkthrough."""


def redact(text: str) -> str:
    """Drop connection strings and credential assignments. Keep the rest."""
    cleaned = _URL_RE.sub("[redacted-url]", str(text))
    cleaned = _SECRET_RE.sub("[redacted]", cleaned)
    return cleaned[:500]


def public_failure(exc: BaseException) -> str:
    return redact(f"{type(exc).__name__}: {exc}")


def selected_backend() -> str:
    raw = os.environ.get("FIT_FINDER_GUIDE_BACKEND", "auto").strip().lower() or "auto"
    if raw not in BACKENDS:
        return "auto"
    return raw


def configured_api_base(root: Path | None = None) -> str:
    override = os.environ.get("FIT_FINDER_PUBLIC_API_URL", "").strip().rstrip("/")
    if override:
        return override
    tree = root or resolve_root()
    public = json.loads((tree / "deploy" / "public.json").read_text())
    return str(public["apiBase"]).rstrip("/")


def links_for(api_base: str) -> dict[str, str]:
    return {
        "api_docs": f"{api_base}/docs",
        "api_health": f"{api_base}/health",
        "demo_page": "https://neelsrejan.github.io/fit-finder/demo/",
        "learning_site": "https://neelsrejan.github.io/fit-finder/",
        "power_bi": "https://neelsrejan.github.io/fit-finder/powerbi/",
        "extracts": "https://neelsrejan.github.io/fit-finder/extracts/",
        "repo": "https://github.com/neelsrejan/fit-finder",
    }


def intro_banner(backend: str) -> str:
    if backend == "synthetic":
        return (
            "CI fallback. These rows are synthetic. They are not the Neon table "
            "and they are not the public UCSD files."
        )
    return (
        "Public UCSD fit reviews. The live table is in Neon when the Render API is awake. "
        "Shopper sessions later in this tour are simulated. Fit is the reviewer's word, not a return."
    )


def load_walkthrough(
    case: ShopperCase,
    *,
    size_index: float | None = None,
    backend: str = "auto",
    api_base: str | None = None,
    timeout: float = 75.0,
    client: Any = None,
    root: Path | None = None,
) -> dict[str, Any]:
    if backend not in BACKENDS:
        raise GuideSourceError(f"unknown backend {backend}")
    tree = root or resolve_root()
    origin = (api_base or configured_api_base(tree)).rstrip("/")
    size = active_size(case, size_index)
    if backend == "synthetic":
        return _synthetic(case, size, origin, tree)
    if backend == "public_artifact":
        return _artifact(case, size, origin, tree, waking=False, api_error=None)
    if backend == "api":
        return _api(case, size, origin, tree, timeout=timeout, client=client)
    try:
        return _api(case, size, origin, tree, timeout=timeout, client=client)
    except Exception as exc:
        detail = str(exc) if isinstance(exc, GuideSourceError) else public_failure(exc)
        snapped = _artifact(case, size, origin, tree, waking=True, api_error=redact(detail))
        snapped["banner"] = (
            "The free API did not answer, so this view uses the committed public-review artifact. "
            "It is not the synthetic fixture. " + snapped["banner"]
        )
        return snapped


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _metrics(root: Path) -> dict[str, Any]:
    folder = root / "docs" / "metrics"
    return {
        "size_model": _read_json(folder / "size_model.json"),
        "recommender": _read_json(folder / "recommender.json"),
        "experiment": _read_json(folder / "ab_simulated.json"),
        "hm": _read_json(folder / "hm_synthetic.json"),
    }


def _local_limits() -> dict[str, str]:
    from fit_finder.hm.adapter import public_hosting_block_reason

    return {
        "hm_public": public_hosting_block_reason(),
        "power_bi_publish": (
            "A free Power BI license cannot create a Publish to web embed code, "
            "and Publish to web does not support report-level DAX measures. "
            "Pro is a paid license, so this project does not use it. "
            "The CSV extracts are the public artifact."
        ),
        "retailer_extension": "The extension does not match retailer hosts.",
        "synthetic_fallback": (
            "The synthetic review fixture and the simulated shopper experiment "
            "stay available for CI and offline runs."
        ),
    }


def _case_dict(case: ShopperCase, size: float) -> dict[str, Any]:
    return {
        "id": case.id,
        "label": case.label,
        "title": case.title,
        "story": case.story,
        "category": case.category,
        "size_index": float(size),
        "height_in": float(case.height_in),
        "weight_lbs": None if case.weight_lbs is None else float(case.weight_lbs),
        "age": None if case.age is None else float(case.age),
        "price": float(case.price),
        "color": case.color,
        "item_id": case.item_id,
    }


def _outcome(case: ShopperCase, size: float, prediction: dict | None, recs: list[dict], metrics: dict) -> list[str]:
    chosen = metrics["chosen_model"]
    test = metrics["test"][chosen]
    directional = (
        f"The neighbor-size nudge's directional accuracy on the test split is "
        f"{metrics['directional_accuracy']:.4f}, which lost to the most-common-fit-size rule at "
        f"{metrics['most_common_size_directional_accuracy']:.4f}. "
        f"The class model is still the one selected, on log loss."
    )
    trust = (
        f"The number that is safe to repeat is the held-out {chosen} test log loss "
        f"{test['log_loss']:.4f} (accuracy {test['accuracy']:.4f}, macro F1 {test['macro_f1']:.4f}). "
        "Do not quote the simulated return lift or the illustrative dollars as store results."
    )
    if prediction is None:
        return [
            f"No size call came back for the {case.title} at size {size:g}, so there is no recommendation to give her.",
            directional,
            trust,
        ]
    top = recs[0]["item_id"] if recs else "none in this category"
    return [
        (
            f"For the {case.title}, size {prediction['ordered_size']:g} looks {prediction['fit_class']} "
            f"with confidence {prediction['confidence']:.0%}."
        ),
        f"Show her size {prediction['recommended_size']:g}. {prediction['size_note']}",
        f"The first similar item is {top}.",
        history_plain(str(prediction.get("history") or "")),
        directional,
        trust,
    ]


def _assemble(
    *,
    backend: str,
    banner: str,
    waking: bool,
    api_error: str | None,
    api_base: str,
    case: ShopperCase,
    size: float,
    health: dict,
    profile: dict,
    prediction: dict | None,
    recommendations: list[dict],
    recommend_note: str,
    limits: dict,
    root: Path,
    call_error: str | None = None,
) -> dict[str, Any]:
    files = _metrics(root)
    return {
        "backend": backend,
        "banner": banner,
        "waking": waking,
        "api_error": api_error,
        "api_base": api_base,
        "links": links_for(api_base),
        "case": _case_dict(case, size),
        "request": predict_body(case, size),
        "health": health,
        "profile": profile,
        "prediction": prediction,
        "recommendations": recommendations,
        "recommend_note": recommend_note,
        "metrics": files["size_model"],
        "recommender": files["recommender"],
        "experiment": files["experiment"],
        "hm": files["hm"],
        "limits": limits,
        "extracts": [dict(row) for row in EXTRACTS],
        "outcome": _outcome(case, size, prediction, recommendations, files["size_model"]),
        "call_error": call_error,
        "history_plain": history_plain(str((prediction or {}).get("history") or "")),
    }


def _profile_from_file(root: Path, reviews_host: str) -> dict[str, Any]:
    profile = _read_json(root / "docs" / "metrics" / "data_profile.json")
    profile = dict(profile)
    profile["reviews_host"] = reviews_host
    profile["hosted_rows"] = None
    profile["review_text_stored"] = not profile.get("review_text_column", True)
    return profile


def _artifact(
    case: ShopperCase,
    size: float,
    api_base: str,
    root: Path,
    *,
    waking: bool,
    api_error: str | None,
) -> dict[str, Any]:
    from fit_finder.model.predict import predict_one
    from fit_finder.recommend.rank import rank_items

    settings_model = root / "models" / "size_model.joblib"
    settings_catalog = root / "models" / "catalog.parquet"
    provenance = _read_json(root / "models" / "provenance.json")
    profile = _profile_from_file(root, "public_artifact")
    bundle = _bundle(str(settings_model))
    payload = predict_body(case, size)
    prediction = predict_one(bundle, payload)
    catalog = _catalog(str(settings_catalog))
    rec_body = recommend_body(case, size, prediction["recommended_size"])
    ranked = rank_items(
        catalog,
        category=rec_body["category"],
        size_index=rec_body["size_index"],
        limit=rec_body["limit"],
        exclude_item_id=rec_body["exclude_item_id"],
        price=rec_body["price"],
        color=rec_body["color"],
    )
    rows = int(profile["rows"])
    banner = (
        f"Committed public-review artifact: {rows:,} reviews in the profile shipped with the model. "
        "This view did not call the live API. It is not the synthetic fixture."
    )
    health = {
        "status": "ok",
        "model_loaded": True,
        "catalog_loaded": True,
        "data_source": provenance.get("source_kind"),
        "training_rows": provenance.get("rows"),
        "reviews_host": "public_artifact",
        "hosted_rows": None,
        "hm_public": "blocked_license_noncommercial_no_redistribution",
        "power_bi_publish": "unavailable_on_free_license",
    }
    return _assemble(
        backend="public_artifact",
        banner=banner,
        waking=waking,
        api_error=api_error,
        api_base=api_base,
        case=case,
        size=size,
        health=health,
        profile=profile,
        prediction=prediction,
        recommendations=_frame_records(ranked),
        recommend_note=(
            "Ranked by historical fit rate and size closeness on the committed catalog. "
            "Price bands are illustrative. UCSD items have no color."
        ),
        limits=_local_limits(),
        root=root,
    )


@lru_cache(maxsize=2)
def _bundle(path: str) -> dict:
    from fit_finder.model.predict import load_bundle

    return load_bundle(Path(path))


@lru_cache(maxsize=2)
def _catalog(path: str):
    import pandas as pd

    return pd.read_parquet(path)


def _frame_records(frame) -> list[dict]:
    rows = []
    for row in frame.to_dict(orient="records"):
        rows.append(
            {
                "item_id": str(row["item_id"]),
                "source": str(row["source"]),
                "category": str(row["category"]),
                "n_reviews": int(row["n_reviews"]),
                "fit_rate": float(row["fit_rate"]),
                "median_fit_size": float(row["median_fit_size"]),
                "score": float(row["score"]),
                "why": str(row["why"]),
                "price_filter": str(row.get("price_filter") or ""),
            }
        )
    return rows


def _synthetic(case: ShopperCase, size: float, api_base: str, root: Path) -> dict[str, Any]:
    from fit_finder.data.synthetic import make_reviews
    from fit_finder.recommend.catalog import build_catalog
    from fit_finder.recommend.rank import rank_items

    frame = make_reviews(n_users=30, reviews_each=4, seed=1)
    shares = frame["fit"].value_counts(normalize=True)
    probabilities = {name: float(shares.get(name, 0.0)) for name in ("small", "fit", "large")}
    label = max(probabilities, key=probabilities.get)
    prediction = {
        "fit_class": label,
        "confidence": probabilities[label],
        "probabilities": probabilities,
        "ordered_size": float(size),
        "recommended_size": float(size),
        "size_note": "Synthetic majority class. This is the CI fallback, not the hosted model.",
        "model": "synthetic_majority",
        "calibrated": False,
        "history": "synthetic_fixture",
    }
    catalog = build_catalog(frame)
    rec_body = recommend_body(case, size, size)
    ranked = rank_items(
        catalog,
        category=rec_body["category"],
        size_index=rec_body["size_index"],
        limit=rec_body["limit"],
        exclude_item_id=rec_body["exclude_item_id"],
        price=rec_body["price"],
        color=rec_body["color"],
    )
    counts = frame["fit"].value_counts().to_dict()
    profile = {
        "rows": int(len(frame)),
        "users": int(frame["user_id"].nunique()),
        "items": int(frame["item_id"].nunique()),
        "by_source": {str(key): int(value) for key, value in frame["source"].value_counts().to_dict().items()},
        "fit": {name: int(counts.get(name, 0)) for name in ("fit", "small", "large")},
        "categories": int(frame["category"].nunique()),
        "source_kind": "synthetic",
        "reviews_host": "synthetic",
        "hosted_rows": None,
        "review_text_stored": False,
    }
    health = {
        "status": "ok",
        "model_loaded": False,
        "catalog_loaded": True,
        "data_source": "synthetic",
        "training_rows": int(len(frame)),
        "reviews_host": "synthetic",
        "hosted_rows": None,
        "hm_public": "blocked_license_noncommercial_no_redistribution",
        "power_bi_publish": "unavailable_on_free_license",
    }
    return _assemble(
        backend="synthetic",
        banner=intro_banner("synthetic"),
        waking=False,
        api_error=None,
        api_base=api_base,
        case=case,
        size=size,
        health=health,
        profile=profile,
        prediction=prediction,
        recommendations=_frame_records(ranked),
        recommend_note="Synthetic catalog. Fit rates are planted by the fixture generator. Not a Neon readout.",
        limits=_local_limits(),
        root=root,
    )


def _api(
    case: ShopperCase,
    size: float,
    api_base: str,
    root: Path,
    *,
    timeout: float,
    client: Any,
) -> dict[str, Any]:
    import httpx

    own = client is None
    http = client or httpx.Client()
    try:
        health = _request(http, "GET", f"{api_base}/health", None, timeout)
        profile_body = _request(http, "GET", f"{api_base}/data/profile", None, timeout)
        payload = predict_body(case, size)
        try:
            prediction = _request(http, "POST", f"{api_base}/predict-size", payload, timeout)
            call_error = None
        except GuideSourceError as exc:
            prediction = None
            call_error = redact(str(exc))
        recommended = None if prediction is None else prediction.get("recommended_size")
        rec_body = recommend_body(case, size, recommended)
        try:
            recs = _request(http, "POST", f"{api_base}/recommend", rec_body, timeout)
            recommendations = list(recs.get("items") or [])
            recommend_note = str(recs.get("note") or "")
        except GuideSourceError as exc:
            recommendations = []
            recommend_note = ""
            extra = redact(str(exc))
            call_error = extra if call_error is None else f"{call_error} {extra}"
        try:
            limits = _request(http, "GET", f"{api_base}/limits", None, timeout)
        except GuideSourceError:
            limits = _local_limits()
    finally:
        if own:
            http.close()

    profile = dict(profile_body.get("profile") or {})
    reviews_host = str(profile_body.get("reviews_host") or health.get("reviews_host") or "not_configured")
    hosted_rows = profile_body.get("hosted_rows")
    if hosted_rows is None and isinstance(profile_body.get("hosted"), dict):
        hosted_rows = profile_body["hosted"].get("rows")
    profile["reviews_host"] = reviews_host
    profile["hosted_rows"] = hosted_rows
    profile["review_text_stored"] = not profile.get("review_text_column", True)
    if reviews_host == "neon" and hosted_rows is not None:
        banner = (
            f"Live Neon table of the public UCSD reviews, read through the Render API. "
            f"{int(hosted_rows):,} hosted rows. Shopper sessions later in this tour are simulated. "
            "Fit is the reviewer's word, not a return."
        )
    else:
        banner = (
            f"The API answered with reviews_host={reviews_host}. "
            "The Neon table is not confirmed on this response. "
            "This view did not switch to the synthetic fixture."
        )
    return _assemble(
        backend="api",
        banner=banner,
        waking=False,
        api_error=None,
        api_base=api_base,
        case=case,
        size=size,
        health=health,
        profile=profile,
        prediction=prediction,
        recommendations=recommendations,
        recommend_note=recommend_note,
        limits=limits,
        root=root,
        call_error=call_error,
    )


def _request(client: Any, method: str, url: str, payload: dict | None, timeout: float) -> dict:
    try:
        response = client.request(method, url, json=payload, timeout=timeout)
    except GuideSourceError:
        raise
    except Exception as exc:
        raise GuideSourceError(public_failure(exc)) from exc
    if response.status_code >= 400:
        path = url.split("://", 1)[-1]
        path = "/" + path.split("/", 1)[-1] if "/" in path else path
        raise GuideSourceError(f"HTTP {response.status_code} for {path}")
    try:
        body = response.json()
    except Exception as exc:
        raise GuideSourceError(public_failure(exc)) from exc
    if not isinstance(body, dict):
        raise GuideSourceError("the API returned a body that is not an object")
    return body


def post_demo_event(api_base: str, case: ShopperCase, *, timeout: float = 75.0, client: Any = None) -> dict:
    """One demo prediction event. The API stores it. This is not store traffic."""
    import httpx

    own = client is None
    http = client or httpx.Client()
    try:
        return _request(
            http,
            "POST",
            f"{api_base.rstrip('/')}/events",
            {
                "event_type": "prediction",
                "session_id": "streamlit-walkthrough",
                "item_id": case.item_id,
                "category": case.category,
                "arm": "recs",
                "metadata": {"surface": "guided-walkthrough"},
            },
            timeout,
        )
    finally:
        if own:
            http.close()
