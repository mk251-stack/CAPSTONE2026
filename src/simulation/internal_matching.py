"""Match opposing pod orders internally before exchange routing."""

from collections.abc import Mapping, Sequence
from typing import Any


def match_orders(
    orders: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return internally matched allocations and residual orders.

    TODO: Specify allocation priority, fair-price convention, and order schema.
    """
    raise NotImplementedError("Internal matching rules are not finalized.")
