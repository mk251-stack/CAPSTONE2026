"""Generate pod orders for simulated trading intervals.

Order distributions, pod composition, and within-day timing remain to be specified.
"""

from collections.abc import Mapping
from typing import Any


def generate_orders(
    *, interval_index: int, config: Mapping[str, Any], rng: Any | None = None
) -> list[dict[str, Any]]:
    """Return orders submitted in one interval under a future order-flow model.

    TODO: Define the order schema and generation assumptions before implementation.
    """
    raise NotImplementedError("Order generation assumptions are not finalized.")
