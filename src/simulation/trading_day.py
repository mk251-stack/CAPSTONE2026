"""Coordinate a single simulated trading day across intervals and policies."""

from collections.abc import Mapping
from typing import Any


def simulate_trading_day(
    *, scenario: Mapping[str, Any], strategy: Any, config: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Run one day and return its recorded state and performance summary.

    TODO: Define scenario, strategy, configuration, and result schemas.
    """
    raise NotImplementedError("The trading-day simulation is not implemented.")
