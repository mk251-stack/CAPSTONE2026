# Planned Methodology

## Scope

The initial study represents one stock over one trading day. The day is divided into five-minute decision intervals. Multiple independent pods submit buy and sell orders, with fast, medium, and slow groups representing different information horizons. The project description gives approximately 50 pods as an example; the exact pod count and composition are not set here.

## Simulation workflow

The intended interval sequence is:

1. Collect pod orders arriving in the interval.
2. Match eligible opposing quantities internally.
3. Compute the residual net order flow for the desk.
4. Update inventory and market-related states using a documented timing convention.
5. Select an exchange trade subject to operational limits.
6. Record activity, costs, inventory, and matching outcomes, then advance to the next interval.

The precise placement of inventory updates and executions within this sequence must be confirmed before implementing accounting equations. Simulation scenarios should be reusable across policies so comparisons use common order-flow realizations wherever possible.

### Initial simulation data and matching interface

The simulation foundation uses typed `Order`, `MatchedQuantity`, `SimulationConfig`, and `DayScenario` structures in `src/simulation/models.py`. Orders have unique IDs and positive `Decimal` share magnitudes; signed order flow is positive for buys and negative for sells. Integer quantities are normalized to `Decimal`, while floats are rejected to avoid binary rounding. `DayScenario` defensively freezes its nested order collections and validates interval placement and ID uniqueness.

`match_orders` is a policy-independent FIFO function that matches only orders in the same interval. It returns pairwise matched quantities and residual `Order` objects, preserving IDs and metadata. Matching converts quantities to integer units at their finest shared decimal scale, so allocations and residuals are exact and independent of Decimal context precision; no tolerance-based rounding is applied. FIFO remains a provisional, deterministic allocation rule; pricing and cross-interval inventory matching are not implemented.

## Baseline strategies

- **No matching / direct routing:** Each pod routes orders directly to the exchange, representing the absence of a central netting desk.
- **Simultaneous matching:** The desk matches opposing orders arriving in the same interval and does not intentionally carry inventory between intervals.
- **Static heuristic:** A simple documented rule trades down inventory subject to the applicable limits. Its threshold, liquidation fraction, and other settings remain to be selected.

## Rolling-horizon MPC

At each five-minute decision point, MPC uses the observed desk state, residual orders, time remaining, operational limits, and a forecast or assumption about future order flow. It chooses a plan over the remaining horizon to minimize expected cumulative cost. Only the first exchange decision is executed. Newly arriving orders and the updated state are then observed and the plan is solved again.

The state may include desk inventory, planned or promised orders, and a representation of remaining market impact. Information-related inventory exposure may be represented separately, potentially by pod speed or order cohort, if justified by available inputs and tractability. The forecasts, state detail, and optimization formulation remain open.

## Cost modeling

Candidate cost categories are exchange fees, immediate market impact, persistent impact from previous exchange executions, inventory holding risk, and information-related adverse selection. Market-impact memory concerns the desk's own previous exchange trades and their continuing effect on execution costs. Adverse selection concerns price movement against inventory held while waiting for offsetting orders, particularly when that inventory originated from more informed or faster traders. The mechanisms should be separately described and tested to avoid conflating or double-counting them.

## Hindsight benchmark

An offline benchmark will optimize a complete simulated day with full knowledge of that day's order arrivals. It is not a real-time policy. Under the same cost assumptions and constraints, it provides an idealized comparison point for measuring the gap between MPC and a plan with perfect information.

## Monte Carlo evaluation

Policies will be run over many simulated days, using common scenarios where practical. The replication count and sensitivity ranges will be selected after runtime is understood. Planned measures include:

- Total daily cost and savings relative to direct routing.
- Internal match rate and exchange-traded volume.
- Inventory path, peak inventory, and time spent holding inventory.
- Results by fast, medium, and slow order groups.
- The cost gap between MPC and hindsight.
- Sensitivity to order-flow similarity, trader mix, impact persistence, inventory capacity, market participation, and risk assumptions.

Uncertainty across simulated days should be reported alongside average performance once the experiment design is set.
