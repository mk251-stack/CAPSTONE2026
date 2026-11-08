"""Signed buying-requirement accounting for the central desk."""


def update_inventory(
    current_inventory: float, residual_net_order: float, exchange_trade: float
) -> float:
    """Return the desk's remaining buying requirement after this decision.

    A positive requirement means the desk is short. Net trader buys and
    external buys are both positive, in shares. Process trader fills before
    the external action. The policy or simulator checks trading limits.
    """
    return current_inventory + residual_net_order - exchange_trade
