"""Local JSONL event log. Rows written here are real requests to this process.

They are not shopper traffic from a store. The simulated experiment lives in
`fit_finder.events.ab` and writes a different file, marked simulated.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path


def append_event(path: Path, payload: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    event_id = str(uuid.uuid4())
    row = {
        "event_id": event_id,
        "simulated": False,
        **payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=str) + "\n")
    return event_id


def read_events(path: Path, limit: int = 100) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows[-limit:]
