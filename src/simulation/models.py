"""Shared typed data structures for the simulation foundation.

Provisional quantity convention: share quantities use ``Decimal`` to preserve
base-10 fractional quantities exactly. Order magnitudes are positive; signed
order flow is positive for buys and negative for sells.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


def _as_decimal_quantity(value: object, *, field_name: str) -> Decimal:
    """Normalize integer quantities and reject binary floats."""
    if isinstance(value, bool):
        raise TypeError(f"{field_name} must be a Decimal or integer, not bool")
    if isinstance(value, int):
        quantity = Decimal(value)
    elif isinstance(value, Decimal):
        quantity = value
    else:
        raise TypeError(f"{field_name} must be a Decimal or integer; floats are not accepted")

    if not quantity.is_finite():
        raise ValueError(f"{field_name} must be finite")
    if quantity <= 0:
        raise ValueError(f"{field_name} must be strictly positive")
    return quantity


class OrderSide(str, Enum):
    """Direction requested by a trading pod."""

    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True, slots=True)
class Order:
    """A pod order for one stock in one simulation interval.

    ``quantity`` is a finite, strictly positive ``Decimal`` share magnitude.
    Integer inputs are converted to ``Decimal``; floats are rejected to prevent
    binary approximation from entering quantity accounting. ``order_id``
    distinguishes orders that otherwise have identical metadata.
    """

    order_id: str
    pod_id: str
    interval: int
    side: OrderSide
    quantity: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.order_id, str) or not self.order_id.strip():
            raise ValueError("order_id must be a non-empty string")
        if not isinstance(self.pod_id, str) or not self.pod_id.strip():
            raise ValueError("pod_id must be a non-empty string")
        if isinstance(self.interval, bool) or not isinstance(self.interval, int):
            raise TypeError("interval must be an integer")
        if self.interval < 0:
            raise ValueError("interval must be non-negative")
        if not isinstance(self.side, OrderSide):
            try:
                object.__setattr__(self, "side", OrderSide(self.side))
            except (TypeError, ValueError) as exc:
                raise ValueError("side must be 'buy' or 'sell'") from exc
        object.__setattr__(
            self,
            "quantity",
            _as_decimal_quantity(self.quantity, field_name="quantity"),
        )

    @property
    def signed_quantity(self) -> Decimal:
        """Return positive quantity for a buy and negative quantity for a sell."""
        if self.side is OrderSide.BUY:
            return self.quantity
        return -self.quantity


@dataclass(frozen=True, slots=True)
class MatchedQuantity:
    """A quantity internally matched between one buy order and one sell order."""

    buy_order: Order
    sell_order: Order
    quantity: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.buy_order, Order) or not isinstance(self.sell_order, Order):
            raise TypeError("buy_order and sell_order must be Order instances")
        if self.buy_order.side is not OrderSide.BUY:
            raise ValueError("buy_order must have side BUY")
        if self.sell_order.side is not OrderSide.SELL:
            raise ValueError("sell_order must have side SELL")
        if self.buy_order.interval != self.sell_order.interval:
            raise ValueError("matched orders must be from the same interval")
        quantity = _as_decimal_quantity(self.quantity, field_name="matched quantity")
        if quantity > self.buy_order.quantity or quantity > self.sell_order.quantity:
            raise ValueError("matched quantity cannot exceed either source order")
        object.__setattr__(self, "quantity", quantity)


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Small shared configuration for an interval-based simulation.

    The interval duration follows the project's five-minute decision cadence.
    The number of intervals and random seed are supplied by the caller; no
    trading-day length or stochastic model is assumed here.
    """

    interval_count: int
    interval_minutes: int = 5
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.interval_count, bool) or not isinstance(self.interval_count, int):
            raise TypeError("interval_count must be an integer")
        if self.interval_count <= 0:
            raise ValueError("interval_count must be positive")
        if isinstance(self.interval_minutes, bool) or not isinstance(self.interval_minutes, int):
            raise TypeError("interval_minutes must be an integer")
        if self.interval_minutes <= 0:
            raise ValueError("interval_minutes must be positive")
        if self.random_seed is not None and (
            isinstance(self.random_seed, bool) or not isinstance(self.random_seed, int)
        ):
            raise TypeError("random_seed must be an integer or None")


@dataclass(frozen=True, slots=True)
class DayScenario:
    """Pre-generated, immutable orders grouped by interval for a simulated day."""

    orders_by_interval: tuple[tuple[Order, ...], ...]
    scenario_id: str | None = None

    def __post_init__(self) -> None:
        try:
            frozen_intervals = tuple(
                tuple(interval_orders) for interval_orders in self.orders_by_interval
            )
        except TypeError as exc:
            raise TypeError("orders_by_interval must be an iterable of order iterables") from exc
        if not frozen_intervals:
            raise ValueError("a day scenario must contain at least one interval")
        object.__setattr__(self, "orders_by_interval", frozen_intervals)

        if self.scenario_id is not None and (
            not isinstance(self.scenario_id, str) or not self.scenario_id.strip()
        ):
            raise ValueError("scenario_id must be None or a non-empty string")

        seen_order_ids: set[str] = set()
        for interval_index, interval_orders in enumerate(frozen_intervals):
            for order in interval_orders:
                if not isinstance(order, Order):
                    raise TypeError("scenario entries must be Order instances")
                if order.interval != interval_index:
                    raise ValueError(
                        "each order interval must match its position in orders_by_interval"
                    )
                if order.order_id in seen_order_ids:
                    raise ValueError("order_id values must be unique within a day scenario")
                seen_order_ids.add(order.order_id)
