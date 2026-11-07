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

- `Order` represents one pod's request in one interval. It stores `pod_id`, zero-based `interval`, `side` (`BUY` or `SELL`), and a positive finite `quantity` magnitude.
- Signed order quantity is positive for a buy and negative for a sell. The unsigned `quantity` remains positive for both sides; use `Order.signed_quantity` when aggregating net flow.
- `SimulationConfig` stores the interval count, the five-minute interval duration, and an optional random seed. No number of intervals or stochastic order parameters is prescribed by this data structure.
- `DayScenario` stores a complete day's orders grouped by interval so later policies can reuse the same realized scenario.
- `match_orders` matches only orders from the same interval. Within each interval, it uses FIFO priority based on the caller-provided sequence, separately for buys and sells. This simple deterministic rule makes matching reproducible; a pro-rata or other allocation rule can replace it later.
- A match records the source buy order, source sell order, and positive matched quantity. Any unmatched remainder is returned as a new order retaining the source pod, interval, and side. The matching function does not set a price, mutate orders, or depend on a trading strategy.

These matching choices are provisional implementation conventions, not calibrated market assumptions. The internal fair-price convention, whether and how older desk inventory is paired with later orders, and the final allocation priority remain open. The initial matcher is scoped to contemporaneous (same-interval) order matching.

## Documentation rule

Numerical examples in project materials must not be treated as calibrated parameters. New assumptions should be recorded with their rationale, status, and the date or meeting at which they are reviewed.
