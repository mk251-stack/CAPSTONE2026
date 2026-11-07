"""Baseline that matches opposing orders arriving in the same interval only."""

from collections.abc import Sequence, Mapping
from typing import Any


def match_simultaneous_orders(
    orders: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    """Return same-interval internal matches and residual exchange orders.

    TODO: Reuse the finalized matching conventions once they are specified.
    """
    raise NotImplementedError("Simultaneous matching baseline is not implemented.")
