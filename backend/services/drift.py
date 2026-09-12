"""Dependency-free score-distribution drift metrics for model monitoring."""
from __future__ import annotations

from math import log
from typing import Iterable


def _histogram(values: list[float], bins: int) -> list[float]:
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, max(0, int(float(value) * bins)))
        counts[index] += 1
    total = max(1, len(values))
    return [count / total for count in counts]


def population_stability_index(reference: Iterable[float], current: Iterable[float], bins: int = 10) -> float:
    ref = _histogram([float(x) for x in reference], bins)
    cur = _histogram([float(x) for x in current], bins)
    eps = 1e-6
    return round(sum((c - r) * log((c + eps) / (r + eps)) for r, c in zip(ref, cur)), 6)


def drift_status(psi: float) -> str:
    if psi >= 0.25:
        return "significant_drift"
    if psi >= 0.10:
        return "watch"
    return "stable"
