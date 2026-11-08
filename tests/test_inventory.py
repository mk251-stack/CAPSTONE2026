"""Checks for the desk's signed buying-requirement convention."""

import pytest

from src.simulation import Order, OrderSide, match_orders
from src.simulation.inventory import update_inventory


@pytest.mark.parametrize(
    ("starting", "net_order", "external", "expected"),
    [
        (0, 60, 30, 30),      # External purchase partially covers a short.
        (0, -60, -30, -30),   # External sale partially reduces a long.
        (60, -60, 0, 0),      # A later trader sale offsets the short.
        (30, -60, -15, -15),  # Trader fills can reverse the desk position.
        (-15, 0, -15, 0),     # A final sale closes the long position.
    ],
)
def test_update_inventory(starting, net_order, external, expected):
    assert update_inventory(starting, net_order, external) == expected


def test_matched_orders_feed_inventory_accounting():
    orders = [
        Order("buyer", 1, OrderSide.BUY, 100),
        Order("seller", 1, OrderSide.SELL, 40),
    ]
    matches, residuals = match_orders(orders)
    net_order = sum(order.signed_quantity for order in residuals)

    assert sum(match.quantity for match in matches) == 40
    assert net_order == 60
    assert update_inventory(0, net_order, 30) == 30
