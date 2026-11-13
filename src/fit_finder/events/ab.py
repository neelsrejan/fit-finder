"""Simulated shoppers, recs versus no recs.

Each shopper has a latent size. The control arm orders with a documented
bias. The treatment arm sometimes accepts a recommendation one size toward
the latent size. A return happens when the received size is not the latent
size, with a small noise flip. Nothing here is observed traffic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from fit_finder.events.assumptions import (
    ALPHA,
    ASSUMED_COST_PER_RETURN,
    N_SHOPPERS,
    P_ACCEPT_RECOMMENDATION,
    P_CLICK_GIVEN_IMPRESSION,
    P_POLICY_RIGHT_ABOUT_DIRECTION,
    P_LABEL_NOISE,
    P_ORDER_TOO_LARGE,
    P_ORDER_TOO_SMALL,
    PLANNING_LIFT_PP,
    POWER,
    SEED,
)
from fit_finder.events.power import sample_size_per_arm

CATEGORIES = ("dress", "top", "jeans", "skirt", "jacket")


@dataclass
class Shopper:
    shopper_id: int
    category: str
    arm: str
    latent_size: int
    ordered_size: int
    received_size: int
    accepted_recommendation: bool
    returned: bool
    clicked: bool


def _order_size(rng: np.random.Generator, latent: int) -> int:
    draw = rng.random()
    if draw < P_ORDER_TOO_SMALL:
        return latent - 1
    if draw < P_ORDER_TOO_SMALL + P_ORDER_TOO_LARGE:
        return latent + 1
    return latent


def _returned(rng: np.random.Generator, latent: int, received: int) -> bool:
    mismatch = received != latent
    if rng.random() < P_LABEL_NOISE:
        mismatch = not mismatch
    return bool(mismatch)


def simulate(n_shoppers: int = N_SHOPPERS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(n_shoppers):
        latent = int(rng.integers(4, 16))
        ordered = _order_size(rng, latent)
        arm = "recs" if index % 2 == 0 else "no_recs"
        accepted = False
        received = ordered
        if arm == "recs" and ordered != latent and rng.random() < P_ACCEPT_RECOMMENDATION:
            # The policy is right about the direction only with the assumed
            # probability. A wrong call moves the shopper further away.
            right = rng.random() < P_POLICY_RIGHT_ABOUT_DIRECTION
            toward = 1 if latent > ordered else -1
            received = ordered + (toward if right else -toward)
            accepted = True
        clicked = arm == "recs" and bool(rng.random() < P_CLICK_GIVEN_IMPRESSION)
        rows.append(
            {
                "shopper_id": index,
                "category": CATEGORIES[index % len(CATEGORIES)],
                "arm": arm,
                "latent_size": latent,
                "ordered_size": ordered,
                "received_size": received,
                "accepted_recommendation": accepted,
                "returned": _returned(rng, latent, received),
                "clicked": clicked,
                "simulated": True,
            }
        )
    return pd.DataFrame(rows)


def summarize(shoppers: pd.DataFrame) -> dict:
    def rate(arm: str) -> float:
        group = shoppers[shoppers["arm"].eq(arm)]
        return float(group["returned"].mean()) if len(group) else 0.0

    control = rate("no_recs")
    treatment = rate("recs")
    impressions = int((shoppers["arm"] == "recs").sum())
    clicks = int(shoppers["clicked"].sum())
    returns_avoided = (control - treatment) * len(shoppers) / 2
    # Planning sample size uses the base rate from the control arm and a
    # 2 point lift, not the lift this particular seed happened to draw.
    planned_treatment = max(0.0, control - PLANNING_LIFT_PP / 100)
    return {
        "simulated": True,
        "n_shoppers": int(len(shoppers)),
        "seed": SEED,
        "return_rate_no_recs": control,
        "return_rate_recs": treatment,
        "lift_pp": (control - treatment) * 100,
        "ctr_recs": (clicks / impressions) if impressions else 0.0,
        "illustrative_dollars": returns_avoided * ASSUMED_COST_PER_RETURN,
        "assumed_cost_per_return": ASSUMED_COST_PER_RETURN,
        "sample_size_per_arm_for_2pp": sample_size_per_arm(control, planned_treatment, ALPHA, POWER),
        "alpha": ALPHA,
        "power": POWER,
        "assumptions": {
            "p_order_too_small": P_ORDER_TOO_SMALL,
            "p_order_too_large": P_ORDER_TOO_LARGE,
            "p_accept_recommendation": P_ACCEPT_RECOMMENDATION,
            "p_policy_right_about_direction": P_POLICY_RIGHT_ABOUT_DIRECTION,
            "p_label_noise": P_LABEL_NOISE,
            "p_click_given_impression": P_CLICK_GIVEN_IMPRESSION,
        },
    }
