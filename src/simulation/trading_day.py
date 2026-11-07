"""Interface for coordinating a typed scenario across a trading day."""

from typing import NoReturn

from .models import DayScenario, SimulationConfig


def simulate_trading_day(
    *, scenario: DayScenario, strategy: object, config: SimulationConfig
) -> NoReturn:
    """Run one day from a validated scenario using a future strategy interface.

    TODO: Define strategy and result contracts before implementing orchestration.
    """
    raise NotImplementedError("The trading-day simulation is not implemented.")
