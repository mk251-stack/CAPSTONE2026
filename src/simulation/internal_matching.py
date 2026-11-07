"""FIFO matching of opposing orders within each simulation interval.

The matching routine is independent of any trading or optimization policy. It
returns pairwise matched quantities and residual orders without mutating inputs.
"""

from collections.abc import Sequence

from .models import MatchedQuantity, Order, OrderSide


def match_orders(
    orders: Sequence[Order],
) -> tuple[list[MatchedQuantity], list[Order]]:
    """Match buy and sell orders in each interval using input-order FIFO priority.

    Orders from different intervals are never matched to one another. Within an
    interval, buys and sells are each consumed in the order they appear in the
    input sequence. Orders may be partially matched; any remaining amount is
    returned as a new :class:`Order` with the original pod, interval, and side.
    The input objects and sequence are not modified.

    Returns:
        A pair ``(matches, residual_orders)``. Each match identifies its source
        buy and sell orders and the positive quantity matched between them.

    Raises:
        TypeError: If an input element is not an :class:`Order`.
    """
    order_list = list(orders)
    for order in order_list:
        if not isinstance(order, Order):
            raise TypeError("orders must contain only Order instances")

    # A dict preserves first-seen interval order, and each index list preserves
    # the caller's order for deterministic FIFO matching.
    interval_indices: dict[int, list[int]] = {}
    for index, order in enumerate(order_list):
        interval_indices.setdefault(order.interval, []).append(index)

    remaining = [float(order.quantity) for order in order_list]
    matches: list[MatchedQuantity] = []

    for indices in interval_indices.values():
        buy_indices = [i for i in indices if order_list[i].side is OrderSide.BUY]
        sell_indices = [i for i in indices if order_list[i].side is OrderSide.SELL]
        buy_position = 0
        sell_position = 0

        while buy_position < len(buy_indices) and sell_position < len(sell_indices):
            buy_index = buy_indices[buy_position]
            sell_index = sell_indices[sell_position]
            matched_amount = min(remaining[buy_index], remaining[sell_index])

            if matched_amount > 0:
                matches.append(
                    MatchedQuantity(
                        buy_order=order_list[buy_index],
                        sell_order=order_list[sell_index],
                        quantity=matched_amount,
                    )
                )
                remaining[buy_index] -= matched_amount
                remaining[sell_index] -= matched_amount

            if remaining[buy_index] <= 0:
                buy_position += 1
            if remaining[sell_index] <= 0:
                sell_position += 1

    residual_orders = [
        Order(
            pod_id=order.pod_id,
            interval=order.interval,
            side=order.side,
            quantity=remaining[index],
        )
        for index, order in enumerate(order_list)
        if remaining[index] > 0
    ]
    return matches, residual_orders
