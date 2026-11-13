"""Download the public UCSD fit-review files. Does not commit them."""

from __future__ import annotations

import urllib.request
from pathlib import Path

# Posted on the McAuley Lab datasets page, Clothing Fit Data section.
# The older deepx.ucsd.edu links on that page are commented out.
SOURCES = {
    "modcloth": "https://mcauleylab.ucsd.edu/public_datasets/data/modcloth/modcloth_final_data.json.gz",
    "renttherunway": "https://mcauleylab.ucsd.edu/public_datasets/data/renttherunway/renttherunway_final_data.json.gz",
}

FILENAMES = {
    "modcloth": "modcloth_final_data.json.gz",
    "renttherunway": "renttherunway_final_data.json.gz",
}


def destination(raw_dir: Path, source: str) -> Path:
    return raw_dir / FILENAMES[source]


def download(raw_dir: Path, source: str, force: bool = False) -> Path:
    """Stream one gzip file into `raw_dir`. Skips the network if the file exists."""
    if source not in SOURCES:
        raise KeyError(f"unknown source {source!r}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = destination(raw_dir, source)
    if path.exists() and path.stat().st_size > 0 and not force:
        return path
    url = SOURCES[source]
    tmp = path.with_suffix(path.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(path)
    return path


def download_all(raw_dir: Path, force: bool = False) -> dict[str, Path]:
    return {name: download(raw_dir, name, force=force) for name in SOURCES}
