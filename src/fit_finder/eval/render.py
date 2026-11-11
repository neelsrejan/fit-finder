"""Write the model card, the eval report, and the resume bullets from JSON.

The prose around the numbers is fixed. The numbers are formatted from
`docs/metrics/*.json`, which the training and simulation scripts write.
"""

from __future__ import annotations

import json
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def render_model_card(metrics: dict) -> str:
    chosen = metrics["chosen_model"]
    test = metrics["test"]
    lines = [
        "# Model card",
        "",
        "The size model predicts the fit feedback a reviewer left: small, fit, or large.",
        "It does not predict a return. The datasets do not have a return flag.",
        "",
        f"Chosen model: **{chosen}**.",
        f"Selection rule: {metrics['selection_rule']}.",
        "",
        "Split counts (reviews):",
        "",
        f"- Train: {metrics['split_counts']['train']}",
        f"- Validation (calibration): {metrics['split_counts']['val']}",
        f"- Test: {metrics['split_counts']['test']}",
        "",
        "Test metrics. Log loss uses the natural log and the three-class probability vector.",
        "",
        "| Model | Log loss | Accuracy | Macro F1 | ECE |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("majority", "logistic", "lightgbm"):
        row = test[name]
        lines.append(
            f"| {name} | {_fmt(row['log_loss'], 4)} | {_fmt(row['accuracy'], 4)} | "
            f"{_fmt(row['macro_f1'], 4)} | {_fmt(row['ece'], 4)} |"
        )
    lines += [
        "",
        "Directional size suggestion on the test rows, using the chosen model.",
        "A correct suggestion stays put when the review said fit, moves up when the review said small, and moves down when the review said large.",
        "",
        f"- Chosen model directional accuracy: {_fmt(metrics['directional_accuracy'], 4)}",
        f"- Most-common-fit-size baseline directional accuracy: {_fmt(metrics['most_common_size_directional_accuracy'], 4)}",
        "",
        "The neighbor-size search lost to that simpler rule on this test split. The class model is still the one selected for the fit label and the confidence. The search is what `/predict-size` returns as `recommended_size`, and this card is where that loss is recorded. Rent the Runway and ModCloth do not share a size scale, which is one reason a two-step nudge in `size_index` is a weak policy.",
        "",
        "Per-category accuracy for the chosen model, largest test categories first.",
        "",
        "| Category | n | Accuracy |",
        "|---|---:|---:|",
    ]
    for row in metrics["per_category"]:
        lines.append(f"| {row['category']} | {row['n']} | {_fmt(row['accuracy'], 4)} |")
    lines += [
        "",
        "Calibration is Platt scaling on the validation split (`CalibratedClassifierCV` with a frozen estimator).",
        "The majority baseline is not calibrated further. Its probabilities are the training class mix.",
        "",
        "Features are measurements, the ordered size, category, and history rates computed from training rows only.",
        "Review text, reviewer name, length, and quality are not inputs.",
        "",
    ]
    return "\n".join(lines)


def render_eval_report(metrics: dict, recommender: dict, ab: dict, hm: dict) -> str:
    chosen = metrics["chosen_model"]
    test = metrics["test"][chosen]
    lines = [
        "# Eval report",
        "",
        "Two kinds of numbers live here. Held-out fit metrics come from the public UCSD reviews.",
        "The shopper experiment and the H&M comparison do not.",
        "",
        "## Held-out fit model",
        "",
        f"Chosen model `{chosen}` test log loss {_fmt(test['log_loss'], 4)}, "
        f"accuracy {_fmt(test['accuracy'], 4)}, macro F1 {_fmt(test['macro_f1'], 4)}, "
        f"ECE {_fmt(test['ece'], 4)}.",
        f"Majority baseline test log loss {_fmt(metrics['test']['majority']['log_loss'], 4)} "
        f"and accuracy {_fmt(metrics['test']['majority']['accuracy'], 4)}.",
        f"Directional accuracy {_fmt(metrics['directional_accuracy'], 4)} versus "
        f"{_fmt(metrics['most_common_size_directional_accuracy'], 4)} for the most-common-fit-size rule.",
        "",
        "## Content ranker",
        "",
        f"Hit rate @{recommender['k']} {_fmt(recommender['hit_rate'], 4)} and MRR {_fmt(recommender['mrr'], 4)} "
        f"on {recommender['n']} held-out fit reviews.",
        recommender["label"] + ".",
        "",
        "## Simulated A/B",
        "",
        "SIMULATED. Not store traffic.",
        "",
        f"Return rate, no recommendations: {_fmt(ab['return_rate_no_recs'], 4)}.",
        f"Return rate, recommendations: {_fmt(ab['return_rate_recs'], 4)}.",
        f"Lift: {_fmt(ab['lift_pp'], 2)} percentage points.",
        f"Recommendation CTR: {_fmt(ab['ctr_recs'], 4)}.",
        f"Illustrative dollars, at ${ab['assumed_cost_per_return']:.0f} assumed per return: {_fmt(ab['illustrative_dollars'], 2)}.",
        f"Sample size per arm to detect a 2 point drop from the control rate, 80% power, alpha 0.05: {ab['sample_size_per_arm_for_2pp']}.",
        "",
        "## H&M comparison",
        "",
        hm["blocked"],
        "",
        f"Synthetic content hit rate @{hm['content']['k']}: {_fmt(hm['content']['hit_rate'], 4)}.",
        f"Synthetic item-item CF hit rate @{hm['collaborative_filtering']['k']}: {_fmt(hm['collaborative_filtering']['hit_rate'], 4)}.",
        hm["note"],
        "",
    ]
    return "\n".join(lines)


def render_resume(metrics: dict, ab: dict) -> str:
    chosen = metrics["chosen_model"]
    test = metrics["test"][chosen]
    majority = metrics["test"]["majority"]
    n = sum(metrics["split_counts"].values())
    return "\n".join(
        [
            "# Resume bullets",
            "",
            "Plain wording for a product, program, or analytics resume. These describe a public portfolio prototype. They do not describe a launched product or real shoppers.",
            "",
            f"- Built a size-and-fit prototype on the public UCSD Rent the Runway and ModCloth fit reviews ({n:,} reviews in the train, validation, and test splits). Compared a most-common-class baseline, logistic regression, and LightGBM, and calibrated the learned models on a validation split. On the held-out test split the chosen model ({chosen}) had log loss {_fmt(test['log_loss'], 3)} and accuracy {_fmt(test['accuracy'], 3)}, against a baseline log loss of {_fmt(majority['log_loss'], 3)} and accuracy of {_fmt(majority['accuracy'], 3)}. A neighbor-size search on that model did not beat recommending the most common fit size in the category. That loss is in the model card.",
            "- Shipped the model behind a local FastAPI service (`/predict-size`, `/recommend`, `/events`) and a Manifest V3 Chrome extension that reads a bundled demo store page. The extension is not pointed at retailer sites.",
            f"- Designed a simulated shopper experiment (recommendations versus none) with a written data-generating process, a two-proportion sample-size calculation, and a Power BI star schema. The simulated return rates were {_fmt(ab['return_rate_no_recs'], 3)} without recommendations and {_fmt(ab['return_rate_recs'], 3)} with recommendations. Dollar figures use an assumed cost per return, not a figure from the datasets.",
            "- Wrote the Power BI data model, DAX measures, and a build guide. The .pbix file is built on a Windows laptop. Publish-to-web is waiting on a free Microsoft account. The H&M purchase-history comparison is implemented against synthetic fixtures and is waiting on a Kaggle API key.",
            "",
            "Do not shorten these into a claim that the prototype served customers, cut returns in production, or used advanced SQL. The SQL in this project is the star-schema grain, not a warehouse job.",
            "",
        ]
    )


def write_all(metrics_dir: Path, docs_dir: Path) -> None:
    metrics = _load(metrics_dir / "size_model.json")
    recommender = _load(metrics_dir / "recommender.json")
    ab = _load(metrics_dir / "ab_simulated.json")
    hm = _load(metrics_dir / "hm_synthetic.json")
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "MODEL_CARD.md").write_text(render_model_card(metrics))
    (docs_dir / "EVAL_REPORT.md").write_text(render_eval_report(metrics, recommender, ab, hm))
    (docs_dir / "RESUME_BULLETS.md").write_text(render_resume(metrics, ab))
