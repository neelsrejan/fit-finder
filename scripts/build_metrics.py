"""Train on the local UCSD parquet, then write every generated number.

Expects data/processed/reviews.parquet. Run `python -m fit_finder.data.pipeline`
first. This script does not download H&M.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fit_finder.analytics.export import build_extracts
from fit_finder.data.clean import clean_directory, write_parquet
from fit_finder.data.download import download_all
from fit_finder.eval.render import write_all
from fit_finder.events.ab import simulate, summarize
from fit_finder.hm.compare import compare
from fit_finder.model.train import bundle_from_result, heldout_scores, public_metrics, save_bundle, train_models, write_metrics
from fit_finder.recommend.catalog import build_catalog
from fit_finder.recommend.evaluate import hit_rate_at_k

ROOT = Path(__file__).resolve().parents[1]


def ensure_parquet(root: Path) -> Path:
    processed = root / "data" / "processed" / "reviews.parquet"
    if processed.exists():
        return processed
    raw = root / "data" / "raw"
    download_all(raw)
    frame = clean_directory(raw)
    write_parquet(frame, processed)
    profile = {
        "rows": int(len(frame)),
        "by_source": frame["source"].value_counts().to_dict(),
        "fit": frame["fit"].value_counts().to_dict(),
        "null_share": {col: float(frame[col].isna().mean()) for col in ("height_in", "weight_lbs", "age", "bust_band")},
    }
    (root / "docs" / "metrics").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "metrics" / "data_profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    return processed


def main() -> None:
    root = ROOT
    parquet = ensure_parquet(root)
    frame = pd.read_parquet(parquet)
    result = train_models(frame)
    metrics = public_metrics(result)
    metrics_dir = root / "docs" / "metrics"
    write_metrics(metrics, metrics_dir / "size_model.json")
    save_bundle(bundle_from_result(result), root / "models" / "size_model.joblib")
    catalog = build_catalog(frame)
    catalog_path = root / "models" / "catalog.parquet"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog.to_parquet(catalog_path, index=False)
    scores = heldout_scores(result)
    score_path = metrics_dir / "heldout_scores.csv"
    scores.to_csv(score_path, index=False)
    recommender = hit_rate_at_k(frame)
    (metrics_dir / "recommender.json").write_text(json.dumps(recommender, indent=2) + "\n")
    ab = summarize(simulate())
    (metrics_dir / "ab_simulated.json").write_text(json.dumps(ab, indent=2) + "\n")
    hm = compare()
    (metrics_dir / "hm_synthetic.json").write_text(json.dumps(hm, indent=2) + "\n")
    build_extracts(root / "analytics" / "extracts", score_path)
    write_all(metrics_dir, root / "docs")
    print(json.dumps({"chosen": metrics["chosen_model"], "test": metrics["test"][metrics["chosen_model"]]}, indent=2))


if __name__ == "__main__":
    main()
