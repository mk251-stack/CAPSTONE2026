
# CAPSTONE2026 — Team Contributions

## Rosario

### Project Definition and Modeling
- Developed the initial project proposal, defining the research objective, project scope, and proposed methodology.
- Established the initial modeling framework: one stock, one trading day, approximately 50 trading pods, and five-minute decision intervals.
- Developed the rolling-horizon Model Predictive Control (MPC) approach, in which the central desk optimizes over the remaining trading day, executes the first decision, updates its state, and re-optimizes.
- Defined the proposed simulation workflow, including order processing, internal matching, residual order calculation, inventory management, and external trading.
- Developed the initial mathematical formulation, including the inventory transition, signed order-flow conventions, candidate objective function, and operational constraints.
- Identified the main cost components: exchange fees, immediate market impact, persistent market impact, inventory holding risk, and information-related adverse selection.
- Proposed an initial approach to modeling persistent market impact and identified key assumptions and open modeling questions.

### Simulation Design
- Established the five-minute interval convention: orders are represented directly at predefined intervals rather than modeled as individual arrivals within each interval.
- Defined the initial order representation, preserving each pod's identity, buy/sell direction, and order quantity.
- Developed numerical examples to validate the expected behavior of internal matching and residual order flow.
- Identified the initial data requirements and modeling assumptions needed to develop the simulation.

### Repository Setup and Implementation
- Created and initialized the CAPSTONE2026 GitHub repository.
- Established the initial project structure, including simulation, optimization, strategy, experiment, documentation, and testing modules.
- Set up the Python project configuration, dependencies, and testing environment.
- Implemented the foundational simulation data structures: `Order`, `OrderSide`, `MatchedQuantity`, `SimulationConfig`, and `DayScenario`.
- Implemented interval-level FIFO internal matching, including partial matches and residual unmatched orders.
- Added validation rules to preserve order information, prevent matching across different intervals, and ensure quantity conservation.
- Developed unit tests to validate the internal matching functionality and its edge cases.


### Liam Mora
- Add contributions here.

### Chuangyi Xu 
- Add contributions here.

