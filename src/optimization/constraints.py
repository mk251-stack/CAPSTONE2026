"""Interfaces for desk inventory and exchange-trading constraints."""

from collections.abc import Mapping
from typing import Any


def describe_constraints(*, config: Mapping[str, Any]) -> list[Any]:
    """Build the optimization constraints for a supplied model configuration.

    TODO: Specify exact constraint forms, units, and end-of-day feasibility rules.
    """
    raise NotImplementedError("Constraint formulations are not finalized.")
