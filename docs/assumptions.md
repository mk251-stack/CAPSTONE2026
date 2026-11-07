# Model Assumptions and Open Decisions

This document separates facts and requirements supplied by the project materials from choices that remain to be made. Items listed as supplied describe the project scope; they do not imply that implementation details or numerical values have been finalized.

## Supplied by the project description

- The model concerns one stock over a single trading day.
- Many independent portfolio managers, also called trading pods, may submit orders for that stock. Approximately 50 is an example, not a required fixed count.
- Pods are grouped conceptually into fast, medium, and slow traders with different information horizons and urgency.
- A central desk receives orders, internally matches opposing orders at a fair price, and sends unmatched quantities to the exchange.
- The desk makes inventory and exchange-trading decisions every five minutes.
- The desk must end each day with zero inventory.
- The desk must respect a maximum inventory limit and an exchange market-participation constraint.
- The desk trades only to reduce inventory exposure and does not speculate for its own account.
- Candidate costs include exchange fees, immediate market impact, persistent impact, inventory risk, and information-related adverse selection.
- Impact is described as size-sensitive, more costly when executed quickly, and temporary; the project description gives roughly 30 minutes for substantial decay as an economic guide, not a finalized decay parameter.
- The evaluation should compare direct routing, simultaneous matching, a heuristic, an advanced planner, and a full-information hindsight benchmark over simulated days.

## Proposed but still preliminary

- A rolling-horizon Model Predictive Control (MPC) approach is the proposed advanced planner. It optimizes over the remaining day, executes only the first decision, then updates and replans.
- A candidate inventory transition is described in the proposal, but its sign convention and event timing have not been fixed.
- A decaying impact state and a decay-kernel formulation are candidate ways to represent market-impact memory. Neither is selected.
- Information-related exposure could be tracked in aggregate or separated by trader speed or order cohort. The required detail is undecided.

## Decisions still to be determined

- Exact pod count and mix; order sizes, signs, arrival processes, correlation, and intraday patterns.
- The order data schema, matching allocation priority, and internal fair-price convention.
- Whether share quantities must be integer-valued or may be fractional, whether one pod may submit opposite-side orders in one interval, and whether explicit order IDs are needed for repeated orders.
- The exact event sequence for arrivals, internal matching, inventory updates, and exchange execution.
- Which future orders or expected fast-trader reversals the desk can forecast, and how forecasts are represented.
- Functional forms and calibrated values for fees, immediate impact, impact persistence, inventory risk, and adverse selection.
- Whether impact memory uses an explicit state, a decay kernel, or another tractable representation, and how its cost enters the objective without double counting.
- Whether inventory-related information exposure is tracked by speed, cohort, or in aggregate.
- Exact inventory and market-participation limits, including market-volume inputs and units.
- The mathematical definition of non-speculative trading and feasibility near the end of day.
- Optimization solver and reliability/runtime targets for the five-minute cycle.
- Monte Carlo replication count, sensitivity ranges, random-seed policy, and reporting intervals.

## Simulation data and matching conventions (provisional)

- `Order` stores a unique `order_id`, `pod_id`, zero-based interval, `OrderSide`, and positive `Decimal` quantity.
- Quantities are share magnitudes and use base-10 `Decimal` arithmetic. Integer inputs are normalized to `Decimal`; floating-point inputs are rejected to prevent binary approximation from entering accounting. This supports fractional quantities exactly. Whether the model should ultimately use whole shares, fractional shares, or a specified share increment remains open.
- Signed order flow is positive for a pod buy and negative for a pod sell. This is a convention for aggregating pod orders; it does not yet establish the central desk's inventory sign convention.
- `SimulationConfig` stores interval count, five-minute interval duration, and an optional random seed. It does not select a day length or stochastic order parameters.
- `DayScenario` stores a complete day's orders by interval. It defensively converts outer and inner collections to tuples, requires at least one interval, validates order types and interval positions, and requires order IDs to be unique within the scenario.
- `match_orders` validates typed inputs and unique IDs, then matches only orders from the same interval. Within each interval, it uses FIFO priority based on caller-provided sequence, separately for buys and sells. Pairwise matches and residuals retain source order IDs. Matching converts all inputs to integer units at their finest shared decimal scale, so allocation and residual arithmetic are exact and do not depend on Decimal context precision or a rounding tolerance.
- Matching assigns no internal price, does not mutate input orders, and is independent of trading or optimization strategy.

FIFO is retained as a simple deterministic provisional allocation rule. It can be replaced if the project selects another priority rule. Whether a pod may submit opposing orders in one interval, whether older desk inventory should offset later orders, the internal fair-price convention, and final share granularity remain open.

## Documentation rule

Numerical examples in project materials must not be treated as calibrated parameters. New assumptions should be recorded with their rationale, status, and the date or meeting at which they are reviewed.
