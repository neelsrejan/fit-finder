"""Step machine for the hiring-manager walkthrough.

Pure functions. The Streamlit view stores a `GuideState` and calls these
on Next, Back, and the suggested prompts. Nothing here reads the network.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from fit_finder.guide.scenario import active_size, get_case


@dataclass(frozen=True)
class Action:
    id: str
    label: str


@dataclass(frozen=True)
class Step:
    number: int
    id: str
    title: str
    doing: str
    why: str
    look_at: str
    actions: tuple[Action, ...]


STEPS: tuple[Step, ...] = (
    Step(
        number=1,
        id="scenario",
        title="The question",
        doing="Introducing one shopper and one garment, before any score is computed.",
        why="The decision is easier to judge once you know what she is holding, and which later numbers are not from a store.",
        look_at="The garment, the size on the page, and the line that separates public reviews from simulated shoppers.",
        actions=(
            Action("start_rivet", "Start with the Rivet dress, size 8"),
            Action("start_gown", "Try a gown in size 4 instead"),
            Action("start_top", "Try a top in size 12 instead"),
        ),
    ),
    Step(
        number=2,
        id="reviews",
        title="The reviews",
        doing="Reading the fit reviews the model was trained on.",
        why="The size call is only as good as this table. Review text and names are not in it.",
        look_at="The row count, the three fit words, and whether this view is the live Neon table.",
        actions=(Action("use_table", "Use this table and pick a size"),),
    ),
    Step(
        number=3,
        id="size",
        title="The size she is considering",
        doing="Packaging the size and the measurements the page would send.",
        why="The model scores a size someone is already considering. It does not invent a body.",
        look_at="Category, size, and height. Price and color stay out of the model. They are used only later, as a labeled filter.",
        actions=(
            Action("size_keep", "Score size {size:g}"),
            Action("size_down", "She is considering a {down:g}"),
            Action("size_up", "She is considering a {up:g}"),
        ),
    ),
    Step(
        number=4,
        id="call",
        title="The size call",
        doing="Scoring small, fit, and large for that size, then checking the nearby sizes.",
        why="Confidence is the probability of the chosen class. The suggested size is the nearby size with a higher chance of the word fit.",
        look_at="The class, the three probabilities, and the one-line size note.",
        actions=(
            Action("show_similar", "Show items with a similar fit"),
            Action("change_size", "Try a different size"),
        ),
    ),
    Step(
        number=5,
        id="similar",
        title="Similar items",
        doing="Ranking other items in the same category by historical fit rate and size closeness.",
        why="Fit rate is the share of public reviews that said fit. It is not a return rate. These items have no color in the public files.",
        look_at="The short list. The price note says the band is illustrative.",
        actions=(Action("show_quality", "Was this model any good?"),),
    ),
    Step(
        number=6,
        id="quality",
        title="Was the model any good",
        doing="Comparing held-out test scores for the majority rule, logistic regression, and LightGBM.",
        why="The service keeps the model with the lowest validation log loss. Accuracy alone hides the small and large classes.",
        look_at="Test log loss. Then the directional line: the neighbor-size nudge lost to the most-common-fit-size rule.",
        actions=(Action("show_simulated", "Which numbers are simulated?"),),
    ),
    Step(
        number=7,
        id="simulated",
        title="What is simulated",
        doing="Showing the shopper experiment and the H&M comparison, which are not the public reviews.",
        why="The lift is readable here, and it is labeled so it is not quoted as store traffic.",
        look_at="The two return rates, the synthetic H&M line, and the Power BI limit. The free license cannot publish the report.",
        actions=(Action("show_outcome", "Give me the recommendation"),),
    ),
    Step(
        number=8,
        id="outcome",
        title="The recommendation",
        doing="Stating the size to show her, and what not to quote.",
        why="The tour ends on a decision, with the caveat in the same step.",
        look_at="The suggested size, the first similar item, and the held-out number that is safe to repeat.",
        actions=(
            Action("explore", "Open free explore"),
            Action("replay", "Walk the Rivet dress again"),
        ),
    ),
)

_BY_NUMBER = {step.number: step for step in STEPS}
_BY_ID = {step.id: step for step in STEPS}


def step_by_number(number: int) -> Step:
    return _BY_NUMBER[number]


def shift_step(current: int, delta: int) -> int:
    nxt = current + delta
    if nxt < 1:
        return 1
    if nxt > len(STEPS):
        return len(STEPS)
    return nxt


@dataclass(frozen=True)
class GuideState:
    step: int = 1
    preset_id: str = "rivet_dress"
    size_index: float | None = None
    explore: bool = False


def action_label(action: Action, state: GuideState) -> str:
    case = get_case(state.preset_id)
    size = active_size(case, state.size_index)
    return action.label.format(size=size, down=max(size - 2, 0), up=size + 2)


def reduce_nav(state: GuideState, delta: int) -> GuideState:
    """Next on the last step opens free explore. Back leaves it."""
    if state.explore and delta < 0:
        return replace(state, explore=False, step=len(STEPS))
    if delta > 0 and state.step >= len(STEPS):
        return replace(state, explore=True)
    return replace(state, step=shift_step(state.step, delta), explore=False)


def reduce_action(state: GuideState, action_id: str) -> GuideState:
    case = get_case(state.preset_id)
    size = active_size(case, state.size_index)
    if action_id == "start_rivet":
        return GuideState(step=2, preset_id="rivet_dress")
    if action_id == "start_gown":
        return GuideState(step=2, preset_id="gown_four")
    if action_id == "start_top":
        return GuideState(step=2, preset_id="top_twelve")
    if action_id == "use_table":
        return replace(state, step=3, explore=False)
    if action_id == "size_keep":
        return replace(state, size_index=size, step=4, explore=False)
    if action_id == "size_down":
        return replace(state, size_index=max(size - 2, 0), step=4, explore=False)
    if action_id == "size_up":
        return replace(state, size_index=size + 2, step=4, explore=False)
    if action_id == "show_similar":
        return replace(state, step=5, explore=False)
    if action_id == "change_size":
        return replace(state, step=3, explore=False)
    if action_id == "show_quality":
        return replace(state, step=6, explore=False)
    if action_id == "show_simulated":
        return replace(state, step=7, explore=False)
    if action_id == "show_outcome":
        return replace(state, step=8, explore=False)
    if action_id == "explore":
        return replace(state, explore=True, step=8)
    if action_id == "replay":
        return GuideState(step=1, preset_id="rivet_dress")
    known = [action.id for step in STEPS for action in step.actions]
    raise KeyError(f"unknown action {action_id!r}; expected one of {', '.join(known)}")


def jump(state: GuideState, number: int) -> GuideState:
    return replace(state, step=shift_step(number, 0), explore=False)
