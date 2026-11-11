"""Turn UCSD JSON lines into one review table.

Rent the Runway and ModCloth do not share a schema. This module keeps the
fields a size model can know before the shopper writes a review, and drops
the review text, the reviewer's name, and post-purchase judgments such as
length and quality.
"""

from __future__ import annotations

import gzip
import json
import math
import re
from pathlib import Path

import pandas as pd

from fit_finder.data.schema import FIT_CLASSES, REVIEW_COLUMNS

_HEIGHT_FOOT = re.compile(r"(\d+)\s*'\s*(\d+)")
_HEIGHT_WORD = re.compile(r"(\d+)\s*ft\s*(\d+)\s*in", re.IGNORECASE)
_NUMBER = re.compile(r"(\d+(?:\.\d+)?)")
_BUST = re.compile(r"(\d+)\s*([a-zA-Z]+)?")

CUP_INDEX = {
    "aa": 0,
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "dd": 5,
    "ddd": 6,
    "e": 6,
    "f": 7,
    "g": 8,
    "h": 9,
    "i": 10,
    "j": 11,
}


def _blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null", "n/a"}


def parse_height(value) -> float | None:
    """Return height in inches. Accepts 5' 8\" and 5ft 6in."""
    if _blank(value):
        return None
    text = str(value).strip()
    match = _HEIGHT_FOOT.search(text) or _HEIGHT_WORD.search(text)
    if not match:
        return None
    feet, inches = int(match.group(1)), int(match.group(2))
    if feet < 3 or feet > 8 or inches < 0 or inches > 11:
        return None
    return float(feet * 12 + inches)


def parse_weight(value) -> float | None:
    if _blank(value):
        return None
    match = _NUMBER.search(str(value))
    if not match:
        return None
    pounds = float(match.group(1))
    if pounds < 70 or pounds > 500:
        return None
    return pounds


def parse_bust(value) -> tuple[float | None, str | None]:
    """Split a bra size such as 34d into band and cup.

    Rent the Runway stores this in one field named "bust size". ModCloth
    splits band ("bra size") and cup ("cup size"). Neither value is a
    tape-measure bust. The model keeps them as band and cup.
    """
    if _blank(value):
        return None, None
    match = _BUST.search(str(value).strip().lower())
    if not match:
        return None, None
    band = float(match.group(1))
    if band < 26 or band > 56:
        band = None
    cup = match.group(2)
    if cup:
        cup = cup.strip().lower()
        if cup not in CUP_INDEX:
            cup = None
    return band, cup


def cup_to_index(cup: str | None) -> float | None:
    if cup is None or _blank(cup):
        return None
    return float(CUP_INDEX.get(str(cup).strip().lower(), math.nan)) if str(cup).strip().lower() in CUP_INDEX else None


def parse_fit(value) -> str | None:
    if _blank(value):
        return None
    label = str(value).strip().lower()
    if label in FIT_CLASSES:
        return label
    return None


def _open_jsonl(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip().rstrip(",")
            if not text or text in {"[", "]"}:
                continue
            yield json.loads(text)


def _text(value, default: str = "unknown") -> str:
    if _blank(value):
        return default
    return str(value).strip().lower()


def _number(value) -> float | None:
    if _blank(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        match = _NUMBER.search(str(value))
        return float(match.group(1)) if match else None


def record_from_renttherunway(raw: dict, row_id: int) -> dict | None:
    fit = parse_fit(raw.get("fit"))
    size = _number(raw.get("size"))
    user = raw.get("user_id")
    item = raw.get("item_id")
    if fit is None or size is None or _blank(user) or _blank(item):
        return None
    band, cup = parse_bust(raw.get("bust size"))
    return {
        "source": "renttherunway",
        "user_id": f"renttherunway:{user}",
        "item_id": f"renttherunway:{item}",
        "category": _text(raw.get("category")),
        "size_raw": str(raw.get("size")).strip(),
        "size_index": size,
        "fit": fit,
        "rating": _number(raw.get("rating")),
        "height_in": parse_height(raw.get("height")),
        "weight_lbs": parse_weight(raw.get("weight")),
        "bust_band": band,
        "cup": cup or "unknown",
        "age": _number(raw.get("age")),
        "body_type": _text(raw.get("body type")),
        "rented_for": _text(raw.get("rented for")),
        "review_date": None if _blank(raw.get("review_date")) else str(raw.get("review_date")).strip(),
        "row_id": row_id,
    }


def record_from_modcloth(raw: dict, row_id: int) -> dict | None:
    fit = parse_fit(raw.get("fit"))
    size = _number(raw.get("size"))
    user = raw.get("user_id")
    item = raw.get("item_id")
    if fit is None or size is None or _blank(user) or _blank(item):
        return None
    band = _number(raw.get("bra size"))
    if band is not None and (band < 26 or band > 56):
        band = None
    cup = _text(raw.get("cup size"), default="")
    cup = cup if cup in CUP_INDEX else "unknown"
    # "bust" on ModCloth is a separate measurement. We do not mix it into the
    # bra band. It is not used as a model feature, because it is missing on
    # Rent the Runway and would make the two sources mean different things.
    return {
        "source": "modcloth",
        "user_id": f"modcloth:{user}",
        "item_id": f"modcloth:{item}",
        "category": _text(raw.get("category")),
        "size_raw": str(raw.get("size")).strip(),
        "size_index": size,
        "fit": fit,
        "rating": _number(raw.get("quality")),
        "height_in": parse_height(raw.get("height")),
        "weight_lbs": None,
        "bust_band": band,
        "cup": cup,
        "age": None,
        "body_type": "unknown",
        "rented_for": "unknown",
        "review_date": None,
        "row_id": row_id,
    }


def load_source(path: Path, source: str) -> pd.DataFrame:
    parser = record_from_renttherunway if source == "renttherunway" else record_from_modcloth
    rows = []
    for row_id, raw in enumerate(_open_jsonl(path)):
        record = parser(raw, row_id)
        if record is not None:
            rows.append(record)
    frame = pd.DataFrame(rows, columns=list(REVIEW_COLUMNS))
    frame["review_date"] = pd.to_datetime(frame["review_date"], errors="coerce")
    return frame


def combine(frames: list[pd.DataFrame]) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame(columns=list(REVIEW_COLUMNS))
    frame = pd.concat(frames, ignore_index=True)
    frame["row_id"] = range(len(frame))
    return frame


def clean_directory(raw_dir: Path) -> pd.DataFrame:
    from fit_finder.data.download import FILENAMES

    frames = []
    for source, name in FILENAMES.items():
        path = raw_dir / name
        if path.exists():
            frames.append(load_source(path, source))
    return combine(frames)


def write_parquet(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return path
