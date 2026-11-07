"""Interface for a transparent, rule-based inventory-management baseline."""

from collections.abc import Mapping
from typing import Any


def choose_heuristic_trade(*, state: Mapping[str, Any], config: Mapping[str, Any]) -> Any:
    """Choose a candidate exchange trade under a documented simple rule.

    TODO: Select and document a heuristic only after relevant limits and timing are
    defined; do not assume a liquidation fraction or threshold in this scaffold.
    """
    raise NotImplementedError("The heuristic policy has not been selected.")
