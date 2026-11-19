"""Plotly figures for one step at a time.

Colors match the Streamlit theme: navy bars on the warm paper background.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

NAVY = "#0B3A5B"
INK = "#1C2830"
ROSE = "#8C2F3B"
SAND = "#C4A574"


def _finish(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=INK)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="sans-serif", size=13),
        margin=dict(l=16, r=16, t=48, b=16),
        height=380,
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E7EEF2")
    return fig


def fit_mix_figure(profile: dict) -> go.Figure:
    order = ["fit", "small", "large"]
    counts = profile.get("fit") or {}
    fig = go.Figure(
        go.Bar(
            x=order,
            y=[int(counts.get(name, 0)) for name in order],
            marker_color=[NAVY, ROSE, SAND],
        )
    )
    return _finish(fig, "Reviews by the word the shopper used")


def probability_figure(prediction: dict) -> go.Figure:
    order = ["small", "fit", "large"]
    probs = prediction.get("probabilities") or {}
    fig = go.Figure(
        go.Bar(
            x=order,
            y=[float(probs.get(name, 0.0)) for name in order],
            marker_color=[ROSE, NAVY, SAND],
        )
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    title = "Calibrated probability of each fit word" if prediction.get("calibrated") else "Share of each fit word"
    return _finish(fig, title)


def fit_rate_figure(recommendations: list[dict]) -> go.Figure:
    labels = [str(row["item_id"]) for row in recommendations]
    rates = [float(row["fit_rate"]) for row in recommendations]
    fig = go.Figure(go.Bar(x=rates, y=labels, orientation="h", marker_color=NAVY))
    fig.update_xaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _finish(fig, "Historical fit rate of the ranked items")


def logloss_figure(metrics: dict) -> go.Figure:
    chosen = metrics["chosen_model"]
    names = ["majority", "logistic", "lightgbm"]
    values = [float(metrics["test"][name]["log_loss"]) for name in names]
    colors = [NAVY if name == chosen else "#9BB4C4" for name in names]
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=colors))
    return _finish(fig, "Held-out test log loss (lower is the selection rule)")


def experiment_figure(experiment: dict) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=["No recommendations", "Recommendations"],
            y=[float(experiment["return_rate_no_recs"]), float(experiment["return_rate_recs"])],
            marker_color=[SAND, NAVY],
        )
    )
    fig.update_yaxes(tickformat=".0%")
    return _finish(fig, "Simulated return rate by arm")


def comparison_frame(metrics: dict) -> pd.DataFrame:
    rows = []
    for name in ("majority", "logistic", "lightgbm"):
        block = metrics["test"][name]
        rows.append(
            {
                "model": name,
                "chosen": "yes" if name == metrics["chosen_model"] else "",
                "log_loss": round(float(block["log_loss"]), 4),
                "accuracy": round(float(block["accuracy"]), 4),
                "macro_f1": round(float(block["macro_f1"]), 4),
                "ece": round(float(block["ece"]), 4),
            }
        )
    return pd.DataFrame(rows)


def request_frame(request: dict) -> pd.DataFrame:
    rows = [{"field": key, "value": "" if value is None else str(value)} for key, value in request.items()]
    return pd.DataFrame(rows)


def recommendation_frame(recommendations: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(recommendations)
    if frame.empty:
        return frame
    show = [column for column in ("item_id", "source", "n_reviews", "fit_rate", "median_fit_size", "score", "why", "price_filter") if column in frame.columns]
    out = frame.loc[:, show].copy()
    if "fit_rate" in out.columns:
        out["fit_rate"] = out["fit_rate"].map(lambda value: round(float(value), 3))
    if "score" in out.columns:
        out["score"] = out["score"].map(lambda value: round(float(value), 3))
    return out


def simulated_table(walk: dict) -> pd.DataFrame:
    experiment = walk["experiment"]
    hm = walk["hm"]
    rows = [
        {
            "piece": "Return rate, no recommendations",
            "value": f"{experiment['return_rate_no_recs']:.1%}",
            "kind": "simulated",
        },
        {
            "piece": "Return rate, recommendations",
            "value": f"{experiment['return_rate_recs']:.1%}",
            "kind": "simulated",
        },
        {
            "piece": "Illustrative dollars at the assumed $20 per return",
            "value": f"{experiment['illustrative_dollars']:.0f}",
            "kind": "simulated",
        },
        {
            "piece": "H&M content hit rate @3",
            "value": f"{hm['content']['hit_rate']:.4f}",
            "kind": "synthetic fixture",
        },
        {
            "piece": "H&M item-item hit rate @3",
            "value": f"{hm['collaborative_filtering']['hit_rate']:.4f}",
            "kind": "synthetic fixture",
        },
    ]
    for extract in walk["extracts"]:
        rows.append({"piece": extract["file"], "value": extract["what"], "kind": extract["kind"]})
    return pd.DataFrame(rows)
