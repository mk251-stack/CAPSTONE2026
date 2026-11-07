"""Unit tests for interval-local internal order matching."""

import pytest

from src.simulation import Order, OrderSide, match_orders


def order(pod_id: str, side: OrderSide, quantity: float, interval: int = 0) -> Order:
    return Order(pod_id=pod_id, interval=interval, side=side, quantity=quantity)


def matched_total(matches) -> float:
    return sum(match.quantity for match in matches)


def test_equal_buy_and_sell_quantities_match_fully() -> None:
    buys = order("pod-buy", OrderSide.BUY, 12)
    sells = order("pod-sell", OrderSide.SELL, 12)

    matches, residuals = match_orders([buys, sells])

    assert matched_total(matches) == 12
    assert len(matches) == 1
    assert matches[0].buy_order == buys
    assert matches[0].sell_order == sells
    assert residuals == []


def test_more_buy_than_sell_leaves_buy_residual() -> None:
    matches, residuals = match_orders(
        [order("buyer", OrderSide.BUY, 15), order("seller", OrderSide.SELL, 9)]
    )

    assert matched_total(matches) == 9
    assert [(item.side, item.quantity) for item in residuals] == [(OrderSide.BUY, 6)]


def test_more_sell_than_buy_leaves_sell_residual() -> None:
    matches, residuals = match_orders(
        [order("buyer", OrderSide.BUY, 4), order("seller", OrderSide.SELL, 11)]
    )

    assert matched_total(matches) == 4
    assert [(item.side, item.quantity) for item in residuals] == [(OrderSide.SELL, 7)]


def test_multiple_orders_on_both_sides_match_fifo() -> None:
    first_buy = order("b1", OrderSide.BUY, 3)
    second_buy = order("b2", OrderSide.BUY, 5)
    first_sell = order("s1", OrderSide.SELL, 4)
    second_sell = order("s2", OrderSide.SELL, 6)

    matches, residuals = match_orders([first_buy, second_buy, first_sell, second_sell])

    assert [(m.buy_order.pod_id, m.sell_order.pod_id, m.quantity) for m in matches] == [
        ("b1", "s1", 3.0),
        ("b2", "s1", 1.0),
        ("b2", "s2", 4.0),
    ]
    assert [(item.pod_id, item.side, item.quantity) for item in residuals] == [
        ("s2", OrderSide.SELL, 2.0)
    ]


def test_partial_match_preserves_original_order_metadata() -> None:
    buy = order("buyer", OrderSide.BUY, 10, interval=2)
    sell = order("seller", OrderSide.SELL, 4, interval=2)

    matches, residuals = match_orders([buy, sell])

    assert matches[0].quantity == 4
    assert residuals == [order("buyer", OrderSide.BUY, 6, interval=2)]


def test_orders_without_opposing_side_remain_unmatched() -> None:
    only_buys = [order("b1", OrderSide.BUY, 2), order("b2", OrderSide.BUY, 7)]

    matches, residuals = match_orders(only_buys)

    assert matches == []
    assert residuals == only_buys


def test_empty_input_returns_empty_results() -> None:
    assert match_orders([]) == ([], [])


def test_quantity_conservation_and_no_match_exceeds_source_order() -> None:
    orders = [
        order("b1", OrderSide.BUY, 7),
        order("s1", OrderSide.SELL, 2),
        order("b2", OrderSide.BUY, 5),
        order("s2", OrderSide.SELL, 6),
        order("b3", OrderSide.BUY, 3, interval=1),
    ]

    matches, residuals = match_orders(orders)

    for source in orders:
        allocated = sum(
            match.quantity
            for match in matches
            if match.buy_order == source or match.sell_order == source
        )
        leftover = sum(
            residual.quantity
            for residual in residuals
            if residual == source
            or (
                residual.pod_id == source.pod_id
                and residual.interval == source.interval
                and residual.side is source.side
            )
        )
        assert allocated <= source.quantity
        assert allocated + leftover == pytest.approx(source.quantity)

    original_signed = sum(item.signed_quantity for item in orders)
    residual_signed = sum(item.signed_quantity for item in residuals)
    assert residual_signed == pytest.approx(original_signed)
    assert matched_total(matches) == pytest.approx(8)


def test_opposing_orders_from_different_intervals_do_not_match() -> None:
    orders = [
        order("buyer", OrderSide.BUY, 5, interval=0),
        order("seller", OrderSide.SELL, 5, interval=1),
    ]

    matches, residuals = match_orders(orders)

    assert matches == []
    assert residuals == orders
