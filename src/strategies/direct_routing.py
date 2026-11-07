"""Baseline in which pod orders are routed directly to the exchange."""

from collections.abc import Sequence, Mapping
from typing import Any


def route_orders_directly(orders: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Return orders for the no-central-matching baseline.

    TODO: Align fee and impact accounting with the common evaluation framework.
    """
    raise NotImplementedError("Direct-routing baseline is not implemented.")
