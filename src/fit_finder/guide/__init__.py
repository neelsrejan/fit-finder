"""Guided hiring-manager walkthrough.

The Streamlit app is a view over this package. Tests call the step machine
and the data assembly without a browser. The synthetic backend is the CI
fallback. The public demo reads Neon through the Render API.
"""

from fit_finder.guide.scenario import CASES, get_case
from fit_finder.guide.steps import STEPS, GuideState, reduce_action, reduce_nav

__all__ = ["CASES", "STEPS", "GuideState", "get_case", "reduce_action", "reduce_nav"]
