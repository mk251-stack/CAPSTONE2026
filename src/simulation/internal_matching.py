"""FIFO matching of opposing orders within each simulation interval.

The matching routine is independent of any trading or optimization policy. It
uses exact integer units derived from Decimal inputs and returns pairwise matches
and residual orders without mutating its inputs.
"""

from collections.abc import Sequence
from decimal import Decimal

from .models import MatchedQuantity, Order, OrderSide


def _to_units(quantity: Decimal, common_exponent: int) -> int:
    """Convert a positive Decimal to exact integer units at a shared scale."""
    decimal_tuple = quantity.as_tuple()
    coefficient = int("".join(str(digit) for digit in decimal_tuple.digits))
    return coefficient * 10 ** (decimal_tuple.exponent - common_exponent)


def _from_units(units: int, common_exponent: int) -> Decimal:
    """Build a Decimal directly from integer units without context rounding."""
    digits = tuple(int(digit) for digit in str(units))
    return Decimal((0, digits, common_exponent))


def match_orders(
    orders: Sequence[Order],
) -> tuple[list[MatchedQuantity], list[Order]]:
    """Match buy and sell orders in each interval using input-order FIFO priority.

    Orders from different intervals are never matched to one another. Within an
    interval, buys and sells are each consumed in the order they appear in the
    input sequence. Orders may be partially matched; any remaining amount is
    returned as a new :class:`Order` with the original ID, pod, interval, and
    side. The input objects and sequence are not modified.

    Returns:
        A pair ``(matches, residual_orders)``. Each match identifies its source
        buy and sell orders and the exact positive Decimal quantity matched.

    Raises:
        TypeError: If an input element is not an :class:`Order`.
        ValueError: If the same order ID appears more than once in the input.
    """
    order_list = list(orders)
    for order in order_list:
        if not isinstance(order, Order):
            raise TypeError("orders must contain only Order instances")

    order_ids = [order.order_id for order in order_list]
    if len(order_ids) != len(set(order_ids)):
        raise ValueError("order_id values must be unique within a matching call")

    # A dict preserves first-seen interval order, and each index list preserves
    # the caller's order for deterministic FIFO matching.
    interval_indices: dict[int, list[int]] = {}
    for index, order in enumerate(order_list):
        interval_indices.setdefault(order.interval, []).append(index)

    if order_list:
        common_exponent = min(
            order.quantity.as_tuple().exponent for order in order_list
        )
        remaining_units = [
            _to_units(order.quantity, common_exponent) for order in order_list
        ]
    else:
        common_exponent = 0
        remaining_units = []
    matches: list[MatchedQuantity] = []

    for indices in interval_indices.values():
        buy_indices = [i for i in indices if order_list[i].side is OrderSide.BUY]
        sell_indices = [i for i in indices if order_list[i].side is OrderSide.SELL]
        buy_position = 0
        sell_position = 0

        while buy_position < len(buy_indices) and sell_position < len(sell_indices):
            buy_index = buy_indices[buy_position]
            sell_index = sell_indices[sell_position]
            matched_units = min(remaining_units[buy_index], remaining_units[sell_index])

            matches.append(
                MatchedQuantity(
                    buy_order=order_list[buy_index],
                    sell_order=order_list[sell_index],
                    quantity=_from_units(matched_units, common_exponent),
                )
            )
            remaining_units[buy_index] -= matched_units
            remaining_units[sell_index] -= matched_units

            if remaining_units[buy_index] == 0:
                buy_position += 1
            if remaining_units[sell_index] == 0:
                sell_position += 1

    residual_orders = [
        Order(
            order_id=order.order_id,
            pod_id=order.pod_id,
            interval=order.interval,
            side=order.side,
            quantity=_from_units(remaining_units[index], common_exponent),
        )
        for index, order in enumerate(order_list)
        if remaining_units[index] > 0
    ]
    return matches, residual_orders
