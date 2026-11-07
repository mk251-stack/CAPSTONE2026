"""Interfaces for assembling expected trading and inventory cost components."""

from collections.abc import Mapping
from typing import Any


def evaluate_cost_components(
    *, state: Mapping[str, Any], decisions: Mapping[str, Any], parameters: Mapping[str, Any]
) -> Mapping[str, float]:
    """Return named cost components for a candidate state and decision.

    TODO: Choose and calibrate functional forms for each cost component.
    """
    raise NotImplementedError("Cost functional forms are not finalized.")
