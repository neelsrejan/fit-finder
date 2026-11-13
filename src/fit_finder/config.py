"""Paths and secrets. A token must never appear in a log line."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings.

    `kaggle_key` is read from the environment so the download path can be
    documented. The default build never calls Kaggle.
    """

    root: Path
    model_path: Path
    catalog_path: Path
    events_path: Path
    kaggle_username: str
    kaggle_key: str
    allow_kaggle_download: bool

    def __repr__(self) -> str:
        key = "set" if self.kaggle_key else "missing"
        user = "set" if self.kaggle_username else "missing"
        return (
            "Settings("
            f"model_path={self.model_path.name}, "
            f"catalog_path={self.catalog_path.name}, "
            f"kaggle_username={user}, kaggle_key={key}, "
            f"allow_kaggle_download={self.allow_kaggle_download})"
        )


def load_settings() -> Settings:
    root = Path(os.environ.get("FIT_FINDER_ROOT", ROOT))
    model = Path(os.environ.get("FIT_FINDER_MODEL", root / "models" / "size_model.joblib"))
    catalog = Path(os.environ.get("FIT_FINDER_CATALOG", root / "models" / "catalog.parquet"))
    events = Path(os.environ.get("FIT_FINDER_EVENTS", root / "data" / "events" / "events.jsonl"))
    return Settings(
        root=root,
        model_path=model,
        catalog_path=catalog,
        events_path=events,
        kaggle_username=os.environ.get("KAGGLE_USERNAME", "").strip(),
        kaggle_key=os.environ.get("KAGGLE_KEY", "").strip(),
        allow_kaggle_download=_flag("FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD"),
    )
