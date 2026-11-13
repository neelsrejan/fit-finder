"""Star-schema extracts for the Power BI report.

`fact_model_score` is a sample of real held-out predictions when that file
has been written by training. Every shopper, click, and dollar row from the
experiment is simulated and carries simulated=true.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fit_finder.events.ab import simulate, summarize
from fit_finder.events.assumptions import ASSUMED_COST_PER_RETURN


def _dates(shoppers: pd.DataFrame) -> pd.DataFrame:
    # Spread the simulated month across March 2024 so a date table exists.
    day = (shoppers["shopper_id"] % 28) + 1
    return pd.to_datetime({"year": 2024, "month": 3, "day": day})


def build_extracts(out_dir: Path, score_path: Path | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    shoppers = simulate()
    summary = summarize(shoppers)
    shoppers = shoppers.copy()
    shoppers["event_date"] = _dates(shoppers)
    shoppers["illustrative_return_cost"] = shoppers["returned"].astype(float) * ASSUMED_COST_PER_RETURN
    shoppers.to_csv(out_dir / "fact_shopper.csv", index=False)

    events = []
    for row in shoppers.itertuples(index=False):
        events.append(
            {
                "event_type": "impression",
                "shopper_id": row.shopper_id,
                "event_date": row.event_date,
                "arm": row.arm,
                "category": row.category,
                "simulated": True,
            }
        )
        if row.arm == "recs":
            events.append(
                {
                    "event_type": "recommendation_impression",
                    "shopper_id": row.shopper_id,
                    "event_date": row.event_date,
                    "arm": row.arm,
                    "category": row.category,
                    "simulated": True,
                }
            )
        if row.clicked:
            events.append(
                {
                    "event_type": "click",
                    "shopper_id": row.shopper_id,
                    "event_date": row.event_date,
                    "arm": row.arm,
                    "category": row.category,
                    "simulated": True,
                }
            )
    pd.DataFrame(events).to_csv(out_dir / "fact_event.csv", index=False)

    dim_date = pd.DataFrame({"event_date": sorted(shoppers["event_date"].unique())})
    dim_date["year"] = dim_date["event_date"].dt.year
    dim_date["month"] = dim_date["event_date"].dt.month
    dim_date["day"] = dim_date["event_date"].dt.day
    dim_date.to_csv(out_dir / "dim_date.csv", index=False)

    categories = set(shoppers["category"].astype(str))
    if score_path and score_path.exists():
        scores = pd.read_csv(score_path) if score_path.suffix == ".csv" else pd.read_parquet(score_path)
        scores.to_csv(out_dir / "fact_model_score.csv", index=False)
        categories = sorted(categories.union(scores["category"].astype(str)))
        summary["model_score_rows"] = int(len(scores))
        summary["model_scores"] = "held-out sample from the trained model"
    else:
        summary["model_score_rows"] = 0
        summary["model_scores"] = "missing"
    pd.DataFrame({"category": sorted(categories)}).to_csv(out_dir / "dim_category.csv", index=False)
    pd.DataFrame(
        {
            "arm": ["recs", "no_recs"],
            "arm_label": ["Recommendations shown (simulated)", "No recommendations (simulated)"],
        }
    ).to_csv(out_dir / "dim_arm.csv", index=False)
    pd.DataFrame(
        [
            {
                "parameter": "assumed_cost_per_return",
                "value": ASSUMED_COST_PER_RETURN,
                "unit": "USD",
                "note": "Assumption. Not from Rent the Runway or ModCloth.",
            }
        ]
    ).to_csv(out_dir / "assumptions.csv", index=False)

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
