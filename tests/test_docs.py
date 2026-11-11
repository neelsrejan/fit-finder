"""The generated writeups stay tied to the metrics JSON."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_card_uses_the_held_out_log_loss():
    metrics = json.loads((ROOT / "docs" / "metrics" / "size_model.json").read_text())
    chosen = metrics["chosen_model"]
    loss = f"{metrics['test'][chosen]['log_loss']:.4f}"
    card = (ROOT / "docs" / "MODEL_CARD.md").read_text()
    assert loss in card
    assert "lost to" in card


def test_eval_report_labels_the_simulation():
    report = (ROOT / "docs" / "EVAL_REPORT.md").read_text()
    assert "SIMULATED" in report
    assert "not downloaded" in report


def test_data_card_matches_the_profile():
    profile = json.loads((ROOT / "docs" / "metrics" / "data_profile.json").read_text())
    card = (ROOT / "docs" / "DATA_CARD.md").read_text()
    assert f"{profile['rows']:,}" in card
