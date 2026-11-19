"""Guided fit-finder walkthrough.

Visual system matches the invalid-agent Streamlit app: warm paper, navy
banner, metric row, one Plotly chart, a table, captions, and suggested
prompts. The order is a step tour. Free explore is the last step.
"""

from __future__ import annotations

import html
import os
from dataclasses import replace
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
import sys

if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from fit_finder.guide.charts import (
    comparison_frame,
    experiment_figure,
    fit_mix_figure,
    fit_rate_figure,
    logloss_figure,
    probability_figure,
    recommendation_frame,
    request_frame,
    simulated_table,
)
from fit_finder.guide.client import (
    configured_api_base,
    intro_banner,
    load_walkthrough,
    post_demo_event,
    redact,
    selected_backend,
)
from fit_finder.guide.scenario import CASES, get_case, history_plain
from fit_finder.guide.steps import STEPS, GuideState, action_label, reduce_action, reduce_nav, step_by_number

_SECRET_NAMES = ("FIT_FINDER_PUBLIC_API_URL", "FIT_FINDER_GUIDE_BACKEND")

_STYLE = """
<style>
.block-container { padding-top: 1.2rem; }
.banner {
  background: #0B3A5B; color: #F7F5F2; padding: 0.7rem 1rem;
  border-radius: 6px; font-size: 0.95rem; margin-bottom: 0.8rem;
}
.stepper { display: flex; gap: 0.35rem; align-items: center; margin: 0.15rem 0 0.35rem; flex-wrap: wrap; }
.pip {
  width: 1.7rem; height: 1.7rem; border-radius: 999px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.8rem; background: #E7EEF2; color: #1C2830;
}
.pip.on { background: #0B3A5B; color: #F7F5F2; }
.pip.done { background: #9BB4C4; color: #F7F5F2; }
.kicker { color: #0B3A5B; font-weight: 650; margin: 0.15rem 0 0.7rem; }
</style>
"""


def apply_streamlit_secrets() -> None:
    """Copy public Streamlit settings into the environment. Existing env wins.

    The Neon URL stays on Render. This function does not read it.
    """
    try:
        secrets = st.secrets
    except Exception:
        return
    for name in _SECRET_NAMES:
        try:
            value = secrets[name]
        except Exception:
            continue
        if value and not os.environ.get(name):
            os.environ[name] = str(value)


def _labels() -> list[str]:
    return [f"Step {step.number}. {step.title}" for step in STEPS]


def _init() -> None:
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("preset_id", "rivet_dress")
    st.session_state.setdefault("size_index", None)
    st.session_state.setdefault("explore", False)
    st.session_state.setdefault("explore_view", "predict")
    st.session_state.setdefault("explore_category", "dress")
    st.session_state.setdefault("explore_size", 8.0)
    st.session_state.setdefault("explore_height", 65.0)
    st.session_state.setdefault("event_note", "")
    st.session_state.setdefault("step_radio", _labels()[0])


def _apply_pending() -> None:
    """Navigation is applied before widgets exist, so Next and the step list agree."""
    pending = st.session_state.pop("pending_state", None)
    if not pending:
        return
    st.session_state.step = int(pending["step"])
    st.session_state.preset_id = pending["preset_id"]
    st.session_state.size_index = pending["size_index"]
    st.session_state.explore = bool(pending["explore"])
    st.session_state.step_radio = _labels()[st.session_state.step - 1]


def _state() -> GuideState:
    return GuideState(
        step=int(st.session_state.step),
        preset_id=str(st.session_state.preset_id),
        size_index=st.session_state.size_index,
        explore=bool(st.session_state.explore),
    )


def _commit(state: GuideState) -> None:
    st.session_state.pending_state = {
        "step": state.step,
        "preset_id": state.preset_id,
        "size_index": state.size_index,
        "explore": state.explore,
    }
    st.rerun()


def _stepper(current: int) -> str:
    pips = []
    for step in STEPS:
        kind = "on" if step.number == current else "done" if step.number < current else "todo"
        pips.append(f'<span class="pip {kind}">{step.number}</span>')
    title = html.escape(step_by_number(current).title)
    return (
        f'<div class="stepper">{"".join(pips)}</div>'
        f'<p class="kicker">Step {current} of {len(STEPS)} · {title}</p>'
    )


@st.cache_data(show_spinner=False)
def _cached_walk(preset_id: str, size_key: str, backend: str, api_base: str) -> dict:
    case = get_case(preset_id)
    size = None if size_key == "" else float(size_key)
    return load_walkthrough(case, size_index=size, backend=backend, api_base=api_base)


def _walk(state: GuideState, backend: str) -> dict:
    api_base = configured_api_base()
    size_key = "" if state.size_index is None else str(state.size_index)
    return _cached_walk(state.preset_id, size_key, backend, api_base)


def _sidebar() -> None:
    with st.sidebar:
        st.header("Walkthrough")
        st.caption("Next and Back keep the order. The list jumps. Free explore is for your own size.")
        st.toggle("Free explore", key="explore")
        labels = _labels()
        picked = st.radio("Step", labels, key="step_radio", label_visibility="collapsed")
        number = labels.index(picked) + 1
        if number != int(st.session_state.step):
            st.session_state.pending_state = {
                "step": number,
                "preset_id": st.session_state.preset_id,
                "size_index": st.session_state.size_index,
                "explore": False,
            }
            st.rerun()


def _banner(text: str) -> None:
    st.markdown(f'<div class="banner">{html.escape(text)}</div>', unsafe_allow_html=True)


def _explain(step) -> None:
    st.markdown(f"**What fit-finder is doing.** {step.doing}")
    st.markdown(f"**Why.** {step.why}")
    st.markdown(f"**What to look at.** {step.look_at}")


def _prompts(state: GuideState) -> None:
    step = step_by_number(state.step)
    st.caption("Suggested prompts")
    columns = st.columns(len(step.actions))
    for column, action in zip(columns, step.actions):
        with column:
            if st.button(action_label(action, state), key=f"act-{step.id}-{action.id}"):
                _commit(reduce_action(state, action.id))


def _nav(state: GuideState) -> None:
    back, forward = st.columns(2)
    with back:
        if st.button("Back", key="nav-back", disabled=state.step == 1 and not state.explore):
            _commit(reduce_nav(state, -1))
    with forward:
        label = "Free explore" if state.step >= len(STEPS) else "Next"
        if st.button(label, key="nav-next", type="primary"):
            _commit(reduce_nav(state, 1))


def _scenario(state: GuideState) -> None:
    case = get_case(state.preset_id)
    st.subheader(case.title)
    st.write(case.story)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category", case.category)
    c2.metric("Size on the page", f"{case.size_index:g}")
    c3.metric("Height", f'{case.height_in:.0f} in')
    c4.metric("Fixture price", f"${case.price:.0f}")
    st.caption(
        "Real, later in the tour: the public reviews, the held-out scores, and the size call. "
        "Simulated, and labeled when you get there: shopper sessions, the experiment, and the dollars. "
        "The H&M file is not in this demo."
    )


def _reviews(walk: dict) -> None:
    profile = walk["profile"]
    host = profile.get("reviews_host")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviews", f'{int(profile["rows"]):,}')
    c2.metric("Shoppers", f'{int(profile.get("users") or 0):,}')
    c3.metric("Items", f'{int(profile.get("items") or 0):,}')
    if host == "neon" and profile.get("hosted_rows") is not None:
        c4.metric("Neon rows", f'{int(profile["hosted_rows"]):,}')
    else:
        c4.metric("Where", str(host))
    st.plotly_chart(fit_mix_figure(profile), width="stretch", config={"displayModeBar": False})
    sources = profile.get("by_source") or {}
    if sources:
        bits = ", ".join(f"{name} {int(count):,}" for name, count in sources.items())
        st.caption(f"Sources: {bits}. Review text is not stored.")
    if walk.get("waking"):
        st.info("The free server did not answer. This is the committed public file, the same training table the API serves when it is awake.")
        if walk.get("api_error"):
            st.caption(redact(str(walk["api_error"])))


def _size(walk: dict) -> None:
    st.dataframe(request_frame(walk["request"]), width="stretch", hide_index=True)
    st.caption("That is the body of the size call. Price and color are not in it.")


def _call(walk: dict) -> None:
    if walk.get("call_error") and walk.get("prediction") is None:
        st.error("The size call did not return. Nothing on this step was invented as a prediction.")
        st.caption(redact(str(walk["call_error"])))
        return
    prediction = walk["prediction"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Looks", prediction["fit_class"])
    c2.metric("Confidence", f'{prediction["confidence"]:.0%}')
    c3.metric("Size she is holding", f'{float(prediction["ordered_size"]):g}')
    c4.metric("Suggested size", f'{float(prediction["recommended_size"]):g}')
    st.plotly_chart(probability_figure(prediction), width="stretch", config={"displayModeBar": False})
    st.caption(prediction["size_note"])
    st.caption(
        f"Model `{prediction['model']}`. Calibrated: {prediction['calibrated']}. "
        f"{history_plain(str(prediction.get('history') or ''))}"
    )


def _similar(walk: dict) -> None:
    rows = walk["recommendations"]
    if not rows:
        st.info("No catalog rows for this category.")
        if walk.get("call_error"):
            st.caption(redact(str(walk["call_error"])))
        return
    st.plotly_chart(fit_rate_figure(rows), width="stretch", config={"displayModeBar": False})
    st.dataframe(recommendation_frame(rows), width="stretch", hide_index=True)
    if walk.get("recommend_note"):
        st.caption(walk["recommend_note"])


def _quality(walk: dict) -> None:
    metrics = walk["metrics"]
    chosen = metrics["chosen_model"]
    test = metrics["test"][chosen]
    c1, c2, c3 = st.columns(3)
    c1.metric("Chosen model", chosen)
    c2.metric("Test log loss", f'{test["log_loss"]:.4f}')
    c3.metric("Test accuracy", f'{test["accuracy"]:.4f}')
    st.plotly_chart(logloss_figure(metrics), width="stretch", config={"displayModeBar": False})
    st.dataframe(comparison_frame(metrics), width="stretch", hide_index=True)
    st.caption(
        f"Directional accuracy {metrics['directional_accuracy']:.4f} versus "
        f"{metrics['most_common_size_directional_accuracy']:.4f} for the most-common-fit-size rule. "
        "The nudge lost. The class model is still the one selected, because the selection rule is log loss."
    )
    if walk["backend"] == "synthetic":
        st.caption("The chart is the committed public-run metrics. It is not a score of the synthetic fixture. The size call on this backend is the synthetic majority class.")
    else:
        training = (walk.get("health") or {}).get("training_rows")
        st.caption(f"Held-out on the public reviews. Training rows on this view: {training}. Content-ranker hit rate @10 is {walk['recommender']['hit_rate']:.4f}.")


def _simulated(walk: dict) -> None:
    st.plotly_chart(experiment_figure(walk["experiment"]), width="stretch", config={"displayModeBar": False})
    st.caption(
        f"SIMULATED. Not store traffic. {int(walk['experiment']['n_shoppers']):,} shoppers, seed {walk['experiment']['seed']}. "
        f"Sample size per arm for a 2 point drop: {int(walk['experiment']['sample_size_per_arm_for_2pp']):,}."
    )
    st.dataframe(simulated_table(walk), width="stretch", hide_index=True)
    st.caption(walk["hm"].get("note") or walk["hm"].get("blocked"))
    st.caption(walk["limits"].get("power_bi_publish", ""))
    links = walk["links"]
    st.markdown(
        f"Power BI note: [{links['power_bi']}]({links['power_bi']}). "
        f"Extracts: [{links['extracts']}]({links['extracts']})."
    )


def _outcome(walk: dict) -> None:
    prediction = walk.get("prediction") or {}
    c1, c2, c3 = st.columns(3)
    if prediction:
        c1.metric("Show her", f'{float(prediction["recommended_size"]):g}')
        c2.metric("Ordered size looks", str(prediction["fit_class"]))
        c3.metric("Confidence", f'{prediction["confidence"]:.0%}')
    else:
        c1.metric("Show her", "—")
    for line in walk["outcome"]:
        st.write(line)
    links = walk["links"]
    st.caption("The fixture page the extension reads, the API, and the learning site stay available.")
    st.markdown(
        f"[Demo fixture]({links['demo_page']}) · "
        f"[API docs]({links['api_docs']}) · "
        f"[Health]({links['api_health']}) · "
        f"[Learning site]({links['learning_site']}) · "
        f"[Repository]({links['repo']})"
    )


_RENDER = {
    "reviews": _reviews,
    "size": _size,
    "call": _call,
    "similar": _similar,
    "quality": _quality,
    "simulated": _simulated,
    "outcome": _outcome,
}


def _guided(state: GuideState, backend: str) -> None:
    step = step_by_number(state.step)
    if step.id == "scenario":
        _banner(intro_banner(backend if backend == "synthetic" else "auto"))
        st.markdown(_stepper(step.number), unsafe_allow_html=True)
        _explain(step)
        _scenario(state)
        _prompts(state)
        _nav(state)
        return
    spinner = "Waking the free server (~1 min) and reading the public reviews…"
    if backend == "synthetic":
        spinner = "Loading the synthetic CI fixture…"
    elif backend == "public_artifact":
        spinner = "Loading the committed public-review artifact…"
    with st.spinner(spinner):
        walk = _walk(state, backend)
    _banner(walk["banner"])
    st.markdown(_stepper(step.number), unsafe_allow_html=True)
    _explain(step)
    _RENDER[step.id](walk)
    _prompts(state)
    _nav(state)


def _apply_explore_case(case_id: str) -> None:
    case = get_case(case_id)
    st.session_state.explore_category = case.category
    st.session_state.explore_size = float(case.size_index)
    st.session_state.explore_height = float(case.height_in)
    st.session_state.preset_id = case.id
    st.session_state.size_index = float(case.size_index)


def _explore(state: GuideState, backend: str) -> None:
    _banner(intro_banner(backend if backend == "synthetic" else "auto"))
    st.subheader("Free explore")
    st.caption("Same service as the tour. Type a size, or use a suggested prompt. One result at a time.")
    prompts = st.columns(3)
    suggested = (
        ("dress8", "Score a dress in size 8", "rivet_dress", "predict"),
        ("health", "What does the API health say?", None, "health"),
        ("limits", "Which numbers are blocked?", None, "limits"),
    )
    for column, (key, label, preset, view) in zip(prompts, suggested):
        with column:
            if st.button(label, key=f"explore-{key}"):
                if preset:
                    _apply_explore_case(preset)
                st.session_state.explore_view = view
                st.rerun()
    with st.form("explore-form"):
        st.text_input("Category", key="explore_category")
        st.number_input("Size", min_value=0.0, max_value=40.0, step=1.0, key="explore_size")
        st.number_input("Height (inches)", min_value=48.0, max_value=84.0, step=1.0, key="explore_height")
        submitted = st.form_submit_button("Score this size")
    if submitted:
        st.session_state.explore_view = "predict"
    view = st.session_state.explore_view
    category = str(st.session_state.explore_category).strip().lower() or "dress"
    case = get_case(state.preset_id)
    custom = replace(
        case,
        category=category,
        size_index=float(st.session_state.explore_size),
        height_in=float(st.session_state.explore_height),
        title=f"{category} size {float(st.session_state.explore_size):g}",
        id=f"explore-{category}",
        item_id=case.item_id,
    )
    if view == "predict":
        with st.spinner("Scoring…"):
            walk = load_walkthrough(
                custom,
                size_index=float(st.session_state.explore_size),
                backend=backend,
                api_base=configured_api_base(),
            )
        _call(walk)
        st.markdown("**Similar items for that size**")
        _similar(walk)
        if walk["backend"] == "api" and st.button("Record this demo view"):
            try:
                recorded = post_demo_event(walk["api_base"], custom)
                st.session_state.event_note = f"Accepted event {recorded.get('event_id')}. This is a demo event, not store traffic."
            except Exception as exc:
                st.session_state.event_note = redact(f"{type(exc).__name__}: {exc}")
        if st.session_state.event_note:
            st.caption(st.session_state.event_note)
    elif view == "health":
        with st.spinner("Reading health…"):
            walk = load_walkthrough(custom, backend=backend, api_base=configured_api_base())
        health = walk["health"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Model loaded", str(health.get("model_loaded")))
        c2.metric("Reviews host", str(health.get("reviews_host")))
        c3.metric("Training rows", f'{int(health.get("training_rows") or 0):,}')
        st.caption(walk["banner"])
        st.caption("Health is summarized. The raw connection string is not on this page.")
    elif view == "limits":
        with st.spinner("Reading limits…"):
            walk = load_walkthrough(custom, backend=backend, api_base=configured_api_base())
        for key in ("hm_public", "power_bi_publish", "retailer_extension", "synthetic_fallback"):
            st.markdown(f"**{key}.** {walk['limits'].get(key, '')}")
    back, _rest = st.columns(2)
    with back:
        if st.button("Back to the recommendation", key="explore-back"):
            _commit(reduce_nav(GuideState(state.step, state.preset_id, state.size_index, True), -1))


def main() -> None:
    apply_streamlit_secrets()
    st.set_page_config(page_title="fit-finder", layout="wide")
    st.markdown(_STYLE, unsafe_allow_html=True)
    _init()
    _apply_pending()
    backend = selected_backend()
    st.title("fit-finder")
    st.caption("A hiring manager walks one size decision, from the public reviews to a recommendation.")
    _sidebar()
    state = _state()
    if state.explore:
        _explore(state, backend)
        return
    _guided(state, backend)


if __name__ == "__main__":
    main()
