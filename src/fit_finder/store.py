"""Hosted Postgres for the cleaned public reviews and demo events.

The connection string is `FIT_FINDER_DATABASE_URL`. This module never logs
that string. The synthetic fixture is not a valid load. H&M competition
files are not a valid load: their license does not allow this public host.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from fit_finder.config import load_settings
from fit_finder.data.schema import REVIEW_COLUMNS

_URL_RE = re.compile(r"postgres(?:ql)?://\S+", re.IGNORECASE)

SCHEMA_SQL = (
    """
    CREATE TABLE IF NOT EXISTS reviews (
        row_id INTEGER PRIMARY KEY,
        source TEXT NOT NULL,
        user_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        category TEXT,
        size_raw TEXT,
        size_index DOUBLE PRECISION,
        fit TEXT,
        rating DOUBLE PRECISION,
        height_in DOUBLE PRECISION,
        weight_lbs DOUBLE PRECISION,
        bust_band DOUBLE PRECISION,
        cup TEXT,
        age DOUBLE PRECISION,
        body_type TEXT,
        rented_for TEXT,
        review_date TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS demo_events (
        event_id TEXT PRIMARY KEY,
        simulated BOOLEAN NOT NULL,
        event_type TEXT,
        session_id TEXT,
        item_id TEXT,
        category TEXT,
        arm TEXT,
        created_at TIMESTAMP NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS load_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
)


def _ensure_schema(cur) -> None:
    for statement in SCHEMA_SQL:
        cur.execute(statement)

COPY_SQL = (
    "COPY reviews ("
    + ", ".join(REVIEW_COLUMNS)
    + ") FROM STDIN"
)


class HostedStoreError(RuntimeError):
    """The hosted database is required and is not usable."""


def database_url() -> str:
    return load_settings().database_url


def require_database_url() -> str:
    """Return the Neon URL or raise a message that names the missing variable.

    The message says where to get a free, no-credit-card database. It does
    not invent a connection string.
    """
    url = database_url()
    if url:
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://") :]
        return url
    raise HostedStoreError(
        "FIT_FINDER_DATABASE_URL is not set. "
        "Create a free Neon project (no credit card; https://neon.com/pricing, Free plan) "
        "and export the direct connection string, the host that does not contain '-pooler'. "
        "Use that string for the pipeline load. The API can use the same string. "
        "Do not commit it and do not paste it into the repository. "
        "Until it is set, the service still scores with the committed model and catalog "
        "trained on the public UCSD reviews, and demo events stay on the local ephemeral file."
    )


def _safe(exc: Exception) -> str:
    text = _URL_RE.sub("postgresql://[redacted]", str(exc))
    return f"{type(exc).__name__}: {text[:400]}"


def _connect():
    url = require_database_url()
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - declared in project dependencies
        raise HostedStoreError(
            "psycopg is not installed. Install the project (pip install -e .) and retry. "
            "The database URL was not printed."
        ) from exc
    try:
        return psycopg.connect(url, connect_timeout=15, autocommit=False)
    except Exception as exc:
        hint = ""
        message = str(exc).lower()
        if "pooler" in url or "prepared" in message or "copy" in message:
            hint = " Use Neon's direct connection string (hostname without '-pooler') for loads."
        raise HostedStoreError(
            "Could not connect to the hosted database. Check FIT_FINDER_DATABASE_URL. "
            "The value was not logged."
            + hint
            + f" Original error: {_safe(exc)}"
        ) from exc


def _cell(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    return value


def assert_public_frame(frame: pd.DataFrame) -> None:
    """Refuse the synthetic fixture and any table that is not the two lab sources."""
    sources = set(frame["source"].astype(str).unique()) if len(frame) else set()
    if len(frame) < 100_000 or sources != {"modcloth", "renttherunway"}:
        raise HostedStoreError(
            f"Refusing to load {len(frame)} rows from sources {sorted(sources)}. "
            "The hosted table is the cleaned public UCSD ModCloth and Rent the Runway "
            "reviews (about 275,334 rows). The synthetic fixture is the CI and offline "
            "fallback and must not be published as the real dataset."
        )
    if "review_text" in frame.columns or "user_name" in frame.columns:
        raise HostedStoreError("Refusing to load review text or reviewer names.")


def load_reviews(frame: pd.DataFrame) -> dict:
    """Replace the hosted review table with the cleaned public frame."""
    assert_public_frame(frame)
    rows = [
        tuple(_cell(value) for value in record)
        for record in frame.loc[:, list(REVIEW_COLUMNS)].itertuples(index=False, name=None)
    ]
    loaded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                _ensure_schema(cur)
                cur.execute("TRUNCATE reviews")
                with cur.copy(COPY_SQL) as copy:
                    for row in rows:
                        copy.write_row(row)
                cur.executemany(
                    "INSERT INTO load_meta (key, value) VALUES (%s, %s) "
                    "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                    [
                        ("rows", str(len(rows))),
                        ("source_kind", "ucsd_public"),
                        ("loaded_at", loaded_at),
                        ("review_text_stored", "false"),
                    ],
                )
            conn.commit()
    except HostedStoreError:
        raise
    except Exception as exc:
        raise HostedStoreError(
            "The hosted load failed before commit. "
            "If the error mentions COPY or prepared statements, switch "
            "FIT_FINDER_DATABASE_URL to Neon's direct connection string "
            "(hostname without '-pooler'). The URL was not logged. "
            f"Original error: {_safe(exc)}"
        ) from exc
    return {"rows": len(rows), "source_kind": "ucsd_public", "loaded_at": loaded_at}


def review_stats() -> dict:
    """Aggregate counts from the hosted table. No row-level measurements."""
    sql = """
        SELECT source, fit, COUNT(*)::bigint
        FROM reviews
        GROUP BY source, fit
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                _ensure_schema(cur)
                cur.execute(sql)
                grouped = [{"source": source, "fit": fit, "n": int(n)} for source, fit, n in cur.fetchall()]
                cur.execute("SELECT key, value FROM load_meta")
                meta = {key: value for key, value in cur.fetchall()}
            conn.commit()
    except HostedStoreError:
        raise
    except Exception as exc:
        raise HostedStoreError(f"Could not read hosted review counts. {_safe(exc)}") from exc
    return {"groups": grouped, "meta": meta, "rows": sum(item["n"] for item in grouped)}


def append_hosted_event(payload: dict) -> str:
    event_id = str(uuid.uuid4())
    created = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                _ensure_schema(cur)
                cur.execute(
                    "INSERT INTO demo_events "
                    "(event_id, simulated, event_type, session_id, item_id, category, arm, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        event_id,
                        False,
                        payload.get("event_type"),
                        payload.get("session_id"),
                        payload.get("item_id"),
                        payload.get("category"),
                        payload.get("arm"),
                        created,
                    ),
                )
            conn.commit()
    except HostedStoreError:
        raise
    except Exception as exc:
        raise HostedStoreError(f"Could not store the demo event. {_safe(exc)}") from exc
    return event_id


def read_hosted_events(limit: int = 20) -> list[dict]:
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                _ensure_schema(cur)
                cur.execute(
                    "SELECT event_id, simulated, event_type, session_id, item_id, category, arm, created_at "
                    "FROM demo_events ORDER BY created_at DESC LIMIT %s",
                    (int(limit),),
                )
                rows = []
                for event_id, simulated, event_type, session_id, item_id, category, arm, created_at in cur.fetchall():
                    rows.append(
                        {
                            "event_id": event_id,
                            "simulated": bool(simulated),
                            "event_type": event_type,
                            "session_id": session_id,
                            "item_id": item_id,
                            "category": category,
                            "arm": arm,
                            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                        }
                    )
            conn.commit()
    except HostedStoreError:
        raise
    except Exception as exc:
        raise HostedStoreError(f"Could not read hosted demo events. {_safe(exc)}") from exc
    return rows
