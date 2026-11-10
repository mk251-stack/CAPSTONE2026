"""Generate typed pod orders for simulated trading intervals.

Order distributions, pod composition, and within-day timing remain to be specified.
"""

from random import Random

from .models import Order, SimulationConfig


def generate_orders(
    *, interval_index: int, config: SimulationConfig, rng: Random | None = None
) -> list[Order]:
    """Return typed orders submitted in one interval under a future order-flow model.

    TODO: Define the order schema and generation assumptions before implementation.
    """
    raise NotImplementedError("Order generation assumptions are not finalized.")
