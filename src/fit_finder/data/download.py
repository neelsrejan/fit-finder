"""Download the public UCSD fit-review files. Does not commit them.

The files are public. This module does not read an API token. A failure
names the URL and the host so a missing network is not mistaken for a
missing account.
"""

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


class PublicDownloadError(RuntimeError):
    """The public lab file could not be fetched. No account is involved."""


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
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "fit-finder-portfolio/0.1 (public research download; +https://github.com/neelsrejan/fit-finder)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                handle.write(chunk)
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        raise PublicDownloadError(
            "Could not download the public UCSD file for "
            f"{source} from {url}. This host does not use an API key. "
            "Check that this machine can reach mcauleylab.ucsd.edu. "
            f"Original error: {type(exc).__name__}: {exc}"
        ) from exc
    if tmp.stat().st_size <= 0:
        tmp.unlink(missing_ok=True)
        raise PublicDownloadError(f"Download of {url} wrote an empty file.")
    tmp.replace(path)
    return path


def download_all(raw_dir: Path, force: bool = False) -> dict[str, Path]:
    return {name: download(raw_dir, name, force=force) for name in SOURCES}
