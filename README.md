# Internal Netting and Inventory Scheduling Across Trading Pods in Multistrategy Funds

A preliminary Python project for studying how a central desk can internally match opposing orders from independent trading pods, manage the resulting inventory, and schedule residual exchange trades over a trading day. The project is part of the INDE 590 MIE Capstone Experience at Rice University (Fall 2026).

> **Model status:** This repository is an early project implementation. It now includes typed order/scenario structures and interval-local internal matching. Order generation, inventory accounting, the full trading-day simulation, and optimization are not implemented yet. The mathematical formulation, timing conventions, parameter values, and impact-memory treatment remain preliminary.

## Problem background

A multistrategy fund may have many independent portfolio managers trading the same stock. Their buy and sell orders can offset one another, but independent routing sends both sides to the exchange, incurring fees and market impact. A central internal netting desk can match opposing orders at a fair internal price and send only unmatched quantities to the exchange.

When opposite orders arrive at different times, the desk may temporarily hold inventory while waiting for a future match. Holding inventory creates price risk and may expose the desk to adverse selection when the originating trader has information. Conversely, trading too quickly on the exchange can increase fees and immediate or persistent market impact. The desk is expected to make decisions at five-minute intervals, remain within inventory and market-participation limits, and end each day with zero inventory.

## Project objectives

The project will use simulation evidence to investigate:

- Cost savings from a central desk compared with direct exchange routing.
- How a rolling-horizon planner compares with simple matching and heuristic policies.
- How close the planner comes to a full-information hindsight benchmark.
- How appropriate waiting and inventory-management decisions vary with trader speed.
- How results change with order-flow patterns, impact persistence, limits, and risk assumptions.

## Proposed methodology

The work is planned in stages:

1. Define the event sequence, inventory accounting, inputs, and assumptions.
2. Build a single-stock, single-day simulation with five-minute decision intervals and pod order flow.
3. Establish direct-routing, simultaneous-matching, and simple heuristic baselines.
4. Formulate a Model Predictive Control (MPC) policy and a hindsight benchmark under consistent assumptions.
5. Compare policies over common Monte Carlo scenarios and run sensitivity analyses.

### Rolling-horizon MPC

At each interval, the desk observes the current state and newly submitted orders, matches opposing orders, computes the residual imbalance, and optimizes planned exchange trades and inventory over the remaining horizon. It executes only the first planned exchange decision. At the next interval it incorporates new observations, updates the state, and solves again. The future-order forecast available to the planner remains to be determined.

### Cost components

The candidate objective includes exchange transaction fees, immediate market impact, persistent market impact, inventory holding risk, and information-related adverse selection. Functional forms, weights, calibration, and any approximations are open design choices.

Market-impact memory represents the continuing effect of the desk's **own previous exchange executions** on later execution costs. Inventory-related adverse selection represents the possibility that prices move against the desk while it holds inventory originating from informed traders. These are distinct mechanisms and will be modeled and evaluated separately where feasible.

## Repository structure

- `src/simulation/`: shared typed order/scenario structures plus order generation, internal matching, inventory accounting, and trading-day workflow.
- `src/optimization/`: cost components, constraints, MPC, and market-impact alternatives.
- `src/strategies/`: direct routing, simultaneous matching, and heuristic baselines.
- `experiments/`: baseline comparisons and sensitivity analyses.
- `tests/`: reserved for focused unit tests as model components are implemented; current placeholders are skipped.
- `docs/methodology.md`: planned workflow and evaluation design.
- `docs/assumptions.md`: supplied assumptions and unresolved modeling choices.
- `docs/meeting_notes/`: project meeting notes.
- `docs/proposal/`: proposal and source project documents.
- `results/figures/` and `results/tables/`: locations for selected, version-controlled outputs.

## Python environment setup

Python 3.11 or newer is required. From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of the `source` command.

## Tests and experiments

Run the test suite from the repository root after activating the environment:

```bash
pytest
```

The initial test files contain skipped placeholders until the relevant components exist. Experiment entry points are planned but not yet implemented; once implemented, run them from the repository root with:

```bash
python experiments/baseline_comparison.py
python experiments/sensitivity_analysis.py
```

## Development note

The mathematical formulation is preliminary. In particular, the market-impact memory, information-risk representation, order forecasts, parameterization, and end-of-day feasibility treatment will be refined and documented as the project develops. No model equations or parameter values are treated as finalized in this scaffold.
