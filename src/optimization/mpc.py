"""Preliminary interfaces for rolling-horizon and hindsight planners."""

from collections.abc import Mapping
from typing import Any


def plan_mpc(*, state: Mapping[str, Any], forecast: Any, config: Mapping[str, Any]) -> Any:
    """Plan over the remaining horizon and return the first exchange decision.

    TODO: Select the state, forecast, optimization model, solver, and result schema.
    """
    raise NotImplementedError("The MPC formulation is not implemented.")


def plan_hindsight(*, scenario: Mapping[str, Any], config: Mapping[str, Any]) -> Any:
    """Compute an offline full-information benchmark for a complete scenario.

    TODO: Define a benchmark consistent with the eventual MPC model and constraints.
    """
    raise NotImplementedError("The hindsight benchmark is not implemented.")
