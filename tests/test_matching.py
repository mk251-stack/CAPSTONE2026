"""Unit tests for exact, interval-local internal order matching."""

from dataclasses import FrozenInstanceError
from decimal import Decimal
from itertools import count

import pytest

from src.simulation import (
    DayScenario,
    MatchedQuantity,
    Order,
    OrderSide,
    SimulationConfig,
    match_orders,
)


_order_ids = count(1)


def order(
    pod_id: str,
    side: OrderSide,
    quantity: int | Decimal,
    interval: int = 0,
    order_id: str | None = None,
) -> Order:
    return Order(
        order_id=order_id or f"test-order-{next(_order_ids)}",
        pod_id=pod_id,
        interval=interval,
        side=side,
        quantity=quantity,
    )


def matched_total(matches: list[MatchedQuantity]) -> Decimal:
    return sum((match.quantity for match in matches), start=Decimal(0))


def test_equal_buy_and_sell_quantities_match_fully() -> None:
    buy = order("pod-buy", OrderSide.BUY, 12)
    sell = order("pod-sell", OrderSide.SELL, 12)

    matches, residuals = match_orders([buy, sell])

    assert matched_total(matches) == Decimal(12)
    assert len(matches) == 1
    assert matches[0].buy_order is buy
    assert matches[0].sell_order is sell
    assert residuals == []


def test_more_buy_than_sell_leaves_buy_residual() -> None:
    matches, residuals = match_orders(
        [order("buyer", OrderSide.BUY, 15), order("seller", OrderSide.SELL, 9)]
    )

    assert matched_total(matches) == Decimal(9)
    assert [(item.side, item.quantity) for item in residuals] == [
        (OrderSide.BUY, Decimal(6))
    ]


def test_more_sell_than_buy_leaves_sell_residual() -> None:
    matches, residuals = match_orders(
        [order("buyer", OrderSide.BUY, 4), order("seller", OrderSide.SELL, 11)]
    )

    assert matched_total(matches) == Decimal(4)
    assert [(item.side, item.quantity) for item in residuals] == [
        (OrderSide.SELL, Decimal(7))
    ]


def test_multiple_orders_on_both_sides_match_fifo() -> None:
    first_buy = order("b1", OrderSide.BUY, 3)
    second_buy = order("b2", OrderSide.BUY, 5)
    first_sell = order("s1", OrderSide.SELL, 4)
    second_sell = order("s2", OrderSide.SELL, 6)

    matches, residuals = match_orders([first_buy, second_buy, first_sell, second_sell])

    assert [
        (match.buy_order.pod_id, match.sell_order.pod_id, match.quantity)
        for match in matches
    ] == [
        ("b1", "s1", Decimal(3)),
        ("b2", "s1", Decimal(1)),
        ("b2", "s2", Decimal(4)),
    ]
    assert [(item.pod_id, item.side, item.quantity) for item in residuals] == [
        ("s2", OrderSide.SELL, Decimal(2))
    ]


def test_partial_match_preserves_order_identity_and_metadata() -> None:
    buy = order("buyer", OrderSide.BUY, 10, interval=2, order_id="buy-2")
    sell = order("seller", OrderSide.SELL, 4, interval=2, order_id="sell-2")

    matches, residuals = match_orders([buy, sell])

    assert matches[0].quantity == Decimal(4)
    assert residuals == [
        Order(
            order_id="buy-2",
            pod_id="buyer",
            interval=2,
            side=OrderSide.BUY,
            quantity=Decimal(6),
        )
    ]


def test_duplicate_metadata_is_preserved_and_fifo_is_unambiguous_by_id() -> None:
    first_buy = order("same-pod", OrderSide.BUY, 1, order_id="buy-1")
    second_buy = order("same-pod", OrderSide.BUY, 1, order_id="buy-2")
    sell = order("seller", OrderSide.SELL, Decimal("1.5"), order_id="sell-1")

    matches, residuals = match_orders([first_buy, second_buy, sell])

    assert [(match.buy_order.order_id, match.quantity) for match in matches] == [
        ("buy-1", Decimal(1)),
        ("buy-2", Decimal("0.5")),
    ]
    assert [(item.order_id, item.quantity) for item in residuals] == [
        ("buy-2", Decimal("0.5"))
    ]


def test_very_small_fractional_quantities_are_matched_exactly() -> None:
    tiny = Decimal("0.0000000000000000000000000000000000001")
    buy = order("buyer", OrderSide.BUY, tiny * 3)
    sell = order("seller", OrderSide.SELL, tiny)

    matches, residuals = match_orders([buy, sell])

    assert matched_total(matches) == tiny
    assert residuals[0].quantity == tiny * 2
    assert residuals[0].quantity + matched_total(matches) == buy.quantity


def test_mixed_decimal_scales_do_not_round_away_small_fill() -> None:
    tiny = Decimal("0.0000000000000000000000000000000000001")
    buy = order("buyer", OrderSide.BUY, Decimal("1"))
    sell = order("seller", OrderSide.SELL, tiny)

    matches, residuals = match_orders([buy, sell])

    assert matches[0].quantity == tiny
    assert residuals[0].quantity == Decimal("0.9999999999999999999999999999999999999")
    assert residuals[0].quantity + matches[0].quantity == buy.quantity


def test_orders_without_opposing_side_remain_unmatched() -> None:
    only_buys = [order("b1", OrderSide.BUY, 2), order("b2", OrderSide.BUY, 7)]

    matches, residuals = match_orders(only_buys)

    assert matches == []
    assert residuals == only_buys


def test_empty_input_returns_empty_results() -> None:
    assert match_orders([]) == ([], [])


def test_quantity_conservation_per_order_and_signed_flow() -> None:
    orders = [
        order("b1", OrderSide.BUY, 7),
        order("s1", OrderSide.SELL, 2),
        order("b2", OrderSide.BUY, 5),
        order("s2", OrderSide.SELL, 6),
        order("b3", OrderSide.BUY, 3, interval=1),
    ]

    matches, residuals = match_orders(orders)
    allocated_by_id = {item.order_id: Decimal(0) for item in orders}
    residual_by_id = {item.order_id: item.quantity for item in residuals}
    for match in matches:
        allocated_by_id[match.buy_order.order_id] += match.quantity
        allocated_by_id[match.sell_order.order_id] += match.quantity
        assert match.quantity <= match.buy_order.quantity
        assert match.quantity <= match.sell_order.quantity

    for source in orders:
        assert allocated_by_id[source.order_id] <= source.quantity
        assert allocated_by_id[source.order_id] + residual_by_id.get(
            source.order_id, Decimal(0)
        ) == source.quantity

    original_signed = sum((item.signed_quantity for item in orders), start=Decimal(0))
    residual_signed = sum((item.signed_quantity for item in residuals), start=Decimal(0))
    assert residual_signed == original_signed
    assert matched_total(matches) == Decimal(8)


def test_opposing_orders_from_different_intervals_do_not_match() -> None:
    orders = [
        order("buyer", OrderSide.BUY, 5, interval=0),
        order("seller", OrderSide.SELL, 5, interval=1),
    ]

    matches, residuals = match_orders(orders)

    assert matches == []
    assert residuals == orders


def test_match_orders_rejects_non_order_input() -> None:
    with pytest.raises(TypeError, match="only Order instances"):
        match_orders([{"pod_id": "buyer"}])  # type: ignore[list-item]


def test_match_orders_rejects_duplicate_order_ids() -> None:
    buy = order("pod", OrderSide.BUY, 2, order_id="duplicate")
    sell = order("other", OrderSide.SELL, 2, order_id="duplicate")

    with pytest.raises(ValueError, match="unique"):
        match_orders([buy, sell])


@pytest.mark.parametrize(
    "quantity",
    [0, -1, Decimal("NaN"), Decimal("Infinity"), 0.1, True],
)
def test_order_rejects_invalid_or_inexact_quantities(quantity: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        order("pod", OrderSide.BUY, quantity)  # type: ignore[arg-type]


def test_day_scenario_freezes_nested_input_sequences() -> None:
    source_order = order("pod", OrderSide.BUY, 1, interval=0)
    original = [[source_order], []]

    scenario = DayScenario(orders_by_interval=original, scenario_id="scenario-1")  # type: ignore[arg-type]
    original[0].clear()

    assert scenario.orders_by_interval == ((source_order,), ())
    with pytest.raises(FrozenInstanceError):
        scenario.scenario_id = "changed"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        scenario.orders_by_interval[0].append(source_order)  # type: ignore[attr-defined]


def test_day_scenario_rejects_interval_mismatch_and_duplicate_ids() -> None:
    wrong_interval = order("pod", OrderSide.BUY, 1, interval=1, order_id="wrong")
    with pytest.raises(ValueError, match="match its position"):
        DayScenario(orders_by_interval=((wrong_interval,), ()))

    first = order("pod", OrderSide.BUY, 1, interval=0, order_id="duplicate")
    second = order("other", OrderSide.SELL, 1, interval=0, order_id="duplicate")
    with pytest.raises(ValueError, match="unique"):
        DayScenario(orders_by_interval=((first, second),))


def test_day_scenario_rejects_empty_scenario_and_non_order_entries() -> None:
    with pytest.raises(ValueError, match="at least one interval"):
        DayScenario(orders_by_interval=())
    with pytest.raises(TypeError, match="Order instances"):
        DayScenario(orders_by_interval=(("not-an-order",),))  # type: ignore[arg-type]


def test_simulation_config_validates_count_and_duration() -> None:
    assert SimulationConfig(interval_count=2).interval_minutes == 5
    with pytest.raises(ValueError, match="interval_count must be positive"):
        SimulationConfig(interval_count=0)
    with pytest.raises(TypeError, match="interval_count must be an integer"):
        SimulationConfig(interval_count=True)  # type: ignore[arg-type]
