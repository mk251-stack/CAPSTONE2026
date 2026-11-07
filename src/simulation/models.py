"""Shared typed data structures for the simulation foundation.

Provisional convention: order quantities are positive magnitudes. A buy order's
signed quantity is positive and a sell order's signed quantity is negative.
"""

from dataclasses import dataclass
from enum import Enum
import math


class OrderSide(str, Enum):
    """Direction requested by a trading pod."""

    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True, slots=True)
class Order:
    """A pod order for one stock in one simulation interval.

    ``quantity`` is a finite, strictly positive share magnitude. Use
    :attr:`signed_quantity` when aggregating buy and sell flow.
    """

    pod_id: str
    interval: int
    side: OrderSide
    quantity: float

    def __post_init__(self) -> None:
        if not self.pod_id:
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
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, (int, float)):
            raise TypeError("quantity must be a number")
        if not math.isfinite(self.quantity) or self.quantity <= 0:
            raise ValueError("quantity must be finite and strictly positive")

    @property
    def signed_quantity(self) -> float:
        """Return positive quantity for a buy and negative quantity for a sell."""
        if self.side is OrderSide.BUY:
            return float(self.quantity)
        return -float(self.quantity)


@dataclass(frozen=True, slots=True)
class MatchedQuantity:
    """A quantity internally matched between one buy order and one sell order."""

    buy_order: Order
    sell_order: Order
    quantity: float

    def __post_init__(self) -> None:
        if self.buy_order.side is not OrderSide.BUY:
            raise ValueError("buy_order must have side BUY")
        if self.sell_order.side is not OrderSide.SELL:
            raise ValueError("sell_order must have side SELL")
        if self.buy_order.interval != self.sell_order.interval:
            raise ValueError("matched orders must be from the same interval")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, (int, float)):
            raise TypeError("matched quantity must be a number")
        if not math.isfinite(self.quantity) or self.quantity <= 0:
            raise ValueError("matched quantity must be finite and strictly positive")
        if self.quantity > self.buy_order.quantity or self.quantity > self.sell_order.quantity:
            raise ValueError("matched quantity cannot exceed either source order")


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
    """Pre-generated orders grouped by interval for a reproducible simulated day."""

    orders_by_interval: tuple[tuple[Order, ...], ...]
    scenario_id: str | None = None

    def __post_init__(self) -> None:
        for interval_index, interval_orders in enumerate(self.orders_by_interval):
            for order in interval_orders:
                if not isinstance(order, Order):
                    raise TypeError("scenario entries must be Order instances")
                if order.interval != interval_index:
                    raise ValueError(
                        "each order interval must match its position in orders_by_interval"
                    )
