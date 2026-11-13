"""Sample size for a two-proportion return-rate test.

The formula is the standard normal approximation. It is here so the number
in the readout is computed, not typed.
"""

from __future__ import annotations

import math


def z_value(probability: float) -> float:
    """Inverse CDF of a standard normal, via a Beasley-Springer/Moro style rational fit.

    Accurate enough for 0.80 and 0.975, which is all this readout uses.
    """
    # Acklam's approximation, public-domain coefficients widely reproduced.
    a = [
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    ]
    b = [
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    ]
    d = [
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    ]
    plow = 0.02425
    phigh = 1 - plow
    if probability <= 0 or probability >= 1:
        raise ValueError("probability must be between 0 and 1")
    if probability < plow:
        q = math.sqrt(-2 * math.log(probability))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if probability > phigh:
        q = math.sqrt(-2 * math.log(1 - probability))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = probability - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def sample_size_per_arm(p_control: float, p_treatment: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Equal-allocation sample size per arm for a two-sided test of two proportions."""
    if p_control == p_treatment:
        return 0
    z_alpha = z_value(1 - alpha / 2)
    z_beta = z_value(power)
    variance = p_control * (1 - p_control) + p_treatment * (1 - p_treatment)
    effect = p_control - p_treatment
    n = (z_alpha + z_beta) ** 2 * variance / effect**2
    return int(math.ceil(n))
