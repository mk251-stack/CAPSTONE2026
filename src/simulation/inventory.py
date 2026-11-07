"""Inventory state and accounting interfaces for the central desk."""


def update_inventory(
    current_inventory: float, residual_net_order: float, exchange_trade: float
) -> float:
    """Compute the next inventory from the current state and interval activity.

    TODO: Confirm event timing and the signed-quantity convention before defining
    the inventory transition.
    """
    raise NotImplementedError("Inventory accounting convention is not finalized.")
