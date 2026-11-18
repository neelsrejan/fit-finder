"""Download the public UCSD reviews, clean them, and optionally load Neon.

CI does not run this module. The synthetic fixture stays the offline fallback.
A missing database URL is a clear stop, not a fake load.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fit_finder.config import load_settings
from fit_finder.data.clean import clean_directory, write_parquet
from fit_finder.data.download import download_all
from fit_finder.store import HostedStoreError, assert_public_frame, load_reviews, require_database_url


def _profile(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "users": int(frame["user_id"].nunique()),
        "items": int(frame["item_id"].nunique()),
        "by_source": {str(key): int(value) for key, value in frame["source"].value_counts().to_dict().items()},
        "fit": {str(key): int(value) for key, value in frame["fit"].value_counts().to_dict().items()},
        "categories": int(frame["category"].nunique()),
        "null_share": {
            col: float(frame[col].isna().mean())
            for col in ("height_in", "weight_lbs", "age", "bust_band", "review_date")
        },
        "review_text_column": False,
        "source_kind": "ucsd_public",
    }


def build_public_frame(raw_dir: Path, force: bool = False) -> pd.DataFrame:
    """Download both lab gzip files and clean them. No token is read."""
    download_all(raw_dir, force=force)
    frame = clean_directory(raw_dir)
    assert_public_frame(frame)
    return frame


def write_profile(root: Path, profile: dict) -> Path:
    path = root / "docs" / "metrics" / "data_profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, indent=2) + "\n")
    provenance = {
        "source_kind": "ucsd_public",
        "rows": profile["rows"],
        "users": profile["users"],
        "items": profile["items"],
        "by_source": profile["by_source"],
        "citation": "Misra, Wan, and McAuley, RecSys 2018",
        "review_text_stored": False,
        "note": (
            "Counts come from the public McAuley Lab files after cleaning. "
            "The synthetic fixture is not this table."
        ),
    }
    dest = root / "models" / "provenance.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(provenance, indent=2) + "\n")
    return path


def run(force_download: bool = False) -> dict:
    settings = load_settings()
    raw = settings.root / "data" / "raw"
    processed = settings.root / "data" / "processed" / "reviews.parquet"
    frame = build_public_frame(raw, force=force_download)
    write_parquet(frame, processed)
    profile = _profile(frame)
    write_profile(settings.root, profile)
    result = {"rows": profile["rows"], "parquet": str(processed), "hosted": False}
    if settings.database_url or settings.require_hosted_store:
        require_database_url()
        loaded = load_reviews(frame)
        result["hosted"] = True
        result["loaded"] = loaded
    else:
        result["hosted_skipped"] = (
            "FIT_FINDER_DATABASE_URL is not set, so the cleaned table was not loaded "
            "into Neon. Re-run after exporting the direct connection string. "
            "Set FIT_FINDER_REQUIRE_HOSTED_STORE=1 to make this a hard failure."
        )
    return result


def main() -> None:
    try:
        print(json.dumps(run(), indent=2))
    except HostedStoreError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
