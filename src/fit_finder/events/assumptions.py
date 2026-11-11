"""Assumptions for the simulated shopper experiment.

None of these numbers were measured on a live store. They are knobs so the
A/B readout, the power calculation, and the Power BI extract can be rebuilt
from code. Change a knob and the extract changes. Do not describe the result
as observed customer behavior.
"""

from __future__ import annotations

SEED = 7
N_SHOPPERS = 8000

# How often a shopper orders a size other than the size that would fit.
P_ORDER_TOO_SMALL = 0.18
P_ORDER_TOO_LARGE = 0.14

# Treatment only. Chance the shopper accepts the recommended size.
P_ACCEPT_RECOMMENDATION = 0.35

# When the shopper accepts, the chance the policy moves toward the latent
# size rather than away from it. This is an assumption of the simulation.
# It is not the held-out directional accuracy of the trained model.
P_POLICY_RIGHT_ABOUT_DIRECTION = 0.60

# Noise that flips an otherwise determined fit label.
P_LABEL_NOISE = 0.05

# Among treatment shoppers who were shown recommendations.
P_CLICK_GIVEN_IMPRESSION = 0.12

# Illustrative dollars per avoided return. Not a cost from either dataset.
ASSUMED_COST_PER_RETURN = 20.0

# Two-sided test of a return-rate difference.
ALPHA = 0.05
POWER = 0.80
# Planning effect used in the sample-size formula, in percentage points.
PLANNING_LIFT_PP = 2.0
