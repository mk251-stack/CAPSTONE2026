"""Candidate interfaces for immediate and persistent market-impact modeling.

Impact-memory alternatives are open research questions; no decay equation or
parameter value is selected in this scaffold.
"""

from collections.abc import Mapping
from typing import Any


def evaluate_market_impact(
    *, trade: float, state: Mapping[str, Any], parameters: Mapping[str, Any]
) -> Mapping[str, float]:
    """Return candidate immediate and memory-related impact costs.

    TODO: Compare a decaying impact state with decay-kernel alternatives and
    determine how to avoid double-counting costs.
    """
    raise NotImplementedError("The impact-memory formulation is not finalized.")
