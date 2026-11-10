"""Inventory accounting interface using exact share quantities."""

from decimal import Decimal


def update_inventory(
    current_inventory: Decimal,
    residual_net_order: Decimal,
    exchange_trade: Decimal,
) -> Decimal:
    """Return the next desk inventory after interval activity.

    TODO: Confirm event timing and the desk-inventory sign convention before
    implementing this transition. Inputs use Decimal share quantities, matching
    the shared order model's exact quantity representation.
    """
    raise NotImplementedError("Inventory accounting convention is not finalized.")
