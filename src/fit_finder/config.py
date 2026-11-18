"""Paths and secrets. A token or database URL must never appear in a log line."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Public origins a hiring manager can open. The API URL is filled in after
# the free host prints one. It is not a secret.
PAGES_ORIGIN = "https://neelsrejan.github.io"
DEMO_PAGE = f"{PAGES_ORIGIN}/fit-finder/demo/"


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _presence(value: str) -> str:
    return "set" if value else "missing"


@dataclass(frozen=True)
class Settings:
    """Runtime settings.

    Secrets are read from the environment. The repr reports set or missing
    and never the value. The default build never calls Kaggle.
    """

    root: Path
    model_path: Path
    catalog_path: Path
    events_path: Path
    provenance_path: Path
    profile_path: Path
    kaggle_username: str
    kaggle_key: str
    allow_kaggle_download: bool
    database_url: str
    require_hosted_store: bool
    public_api_url: str

    def __repr__(self) -> str:
        return (
            "Settings("
            f"model_path={self.model_path.name}, "
            f"catalog_path={self.catalog_path.name}, "
            f"kaggle_username={_presence(self.kaggle_username)}, "
            f"kaggle_key={_presence(self.kaggle_key)}, "
            f"allow_kaggle_download={self.allow_kaggle_download}, "
            f"database_url={_presence(self.database_url)}, "
            f"require_hosted_store={self.require_hosted_store}, "
            f"public_api_url={_presence(self.public_api_url)})"
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
        provenance_path=Path(os.environ.get("FIT_FINDER_PROVENANCE", root / "models" / "provenance.json")),
        profile_path=Path(os.environ.get("FIT_FINDER_PROFILE", root / "docs" / "metrics" / "data_profile.json")),
        kaggle_username=os.environ.get("KAGGLE_USERNAME", "").strip(),
        kaggle_key=os.environ.get("KAGGLE_KEY", "").strip(),
        allow_kaggle_download=_flag("FIT_FINDER_ALLOW_KAGGLE_DOWNLOAD"),
        database_url=os.environ.get("FIT_FINDER_DATABASE_URL", "").strip(),
        require_hosted_store=_flag("FIT_FINDER_REQUIRE_HOSTED_STORE"),
        public_api_url=os.environ.get("FIT_FINDER_PUBLIC_API_URL", "").strip().rstrip("/"),
    )
