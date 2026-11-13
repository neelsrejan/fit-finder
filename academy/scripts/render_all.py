#!/usr/bin/env python3
"""Render narration YAML files that do not yet have an MP4."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACADEMY = ROOT / "academy"
sys.path.insert(0, str(ACADEMY))

from render_walkthrough import render  # noqa: E402


def main() -> None:
    wanted = list(range(1, 11))
    out_root = ACADEMY / "build" / "videos"
    durations_path = ACADEMY / "content" / "durations.json"
    durations = json.loads(durations_path.read_text()) if durations_path.exists() else {}
    for n in wanted:
        folder = ACADEMY / "narration" / f"session-{n}"
        scripts = sorted(folder.glob("*.yaml"))
        if not scripts:
            raise SystemExit(f"no narration in {folder}")
        for script in scripts:
            dest = out_root / f"session-{n}" / f"{script.stem}.mp4"
            if dest.exists() and dest.stat().st_size > 50_000 and "--force" not in sys.argv:
                print(f"keep {dest}")
            else:
                info = render(script, dest)
                durations[f"session-{n}/{script.stem}"] = info["seconds"]
                durations_path.write_text(json.dumps(durations, indent=2) + "\n")
    print(f"durations {durations_path}")


if __name__ == "__main__":
    main()
