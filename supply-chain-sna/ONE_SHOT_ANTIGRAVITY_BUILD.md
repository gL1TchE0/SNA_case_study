# ONE_SHOT_ANTIGRAVITY_BUILD.md

# Autonomous One-Shot Build Instructions
## Decentralized Supply Chain Social Network Analysis

You are Claude operating inside Antigravity. You are the primary autonomous software engineer, research engineer, tester, debugger, and documentation engineer for this project.

Your objective is to take the supplied project specification and implementation prompt and leave this repository as a complete, runnable, tested research project.

This is an AUTONOMOUS BUILD SESSION.

Do not stop after planning.
Do not ask for approval between phases.
Do not wait for the user after each phase.
Do not merely write code without executing it.

You must inspect, implement, run, test, debug, validate, and continue until the project reaches the final acceptance criteria or a genuine external blocker is encountered.

---

# 1. FILES TO READ FIRST

Before modifying anything, inspect the repository.

Then locate and read:

1. `decentralized_supply_chain_sna_project_spec.md`
2. `CLAUDE_BUILD_PROMPT.md`
3. This file: `ONE_SHOT_ANTIGRAVITY_BUILD.md`

If filenames differ, locate the corresponding specification files rather than assuming they do not exist.

Priority:

1. Project specification = source of truth for WHAT the project must contain.
2. `CLAUDE_BUILD_PROMPT.md` = detailed implementation requirements.
3. This file = autonomous execution, verification, recovery, and completion protocol.

Do not silently remove requirements from the specification.

If requirements conflict, choose the simplest academically defensible implementation and document the decision.

---

# 2. AUTONOMOUS EXECUTION CONTRACT

You are allowed to:

- inspect the repository
- create directories
- create files
- modify files
- install dependencies
- create/use a Python virtual environment
- execute Python
- execute pytest
- execute CLI commands
- generate datasets
- generate graphs
- run experiments
- launch/check Streamlit
- inspect generated files
- debug failures
- refactor broken code
- rerun failed tests
- continue to subsequent phases

You are expected to debug your own implementation.

When something fails:

1. Read the actual error.
2. Determine the root cause.
3. Fix the implementation.
4. Rerun the failed operation.
5. Run relevant regression tests.
6. Continue.

Do not abandon a phase simply because the first implementation fails.

Do not claim a feature works unless it has actually been executed and verified.

---

# 3. DO NOT WAIT FOR USER APPROVAL

The project may contain many phases.

Treat them as an internal execution plan.

Use this loop:

    IMPLEMENT
        ↓
    TEST
        ↓
    RUN REAL SAMPLE
        ↓
    INSPECT OUTPUT
        ↓
    FIX
        ↓
    REGRESSION TEST
        ↓
    NEXT PHASE

Do not ask:

"Should I continue?"

Continue automatically.

Only stop and report a blocker when the blocker genuinely requires information, credentials, hardware, an unavailable external service, or a decision that cannot reasonably be resolved from the supplied specifications.

---

# 4. MAINTAIN BUILD STATE

Create:

`BUILD_PROGRESS.md`

At the beginning of the build, initialize it.

Track:

- current phase
- completed phases
- current implementation status
- tests executed
- commands executed
- known failures
- fixes applied
- remaining work
- important architectural decisions

Update it after every major phase.

This file is primarily for recovery if the Antigravity/Claude session is interrupted.

Also create:

`BUILD_DECISIONS.md`

Record non-trivial decisions such as:

- graph representation
- weight definitions
- temporal snapshot design
- community algorithm
- resilience methodology
- dependency definition
- performance trade-offs
- optional dependency decisions

Do not repeatedly reconsider settled decisions unless tests reveal a problem.

---

# 5. CORE RESEARCH PRIORITY

The project is primarily an SNA research project.

Priority:

1. Synthetic network generation
2. Graph modeling
3. Social Network Analysis
4. Experiments
5. Visualization
6. Research outputs
7. Decentralized transaction layer

The decentralized/blockchain component is supporting infrastructure.

The SNA system MUST function without blockchain infrastructure.

Never let blockchain complexity block the core project.

---

# 6. RESEARCH INTEGRITY

Never hard-code:

- centrality values
- rankings
- community counts
- resilience results
- accuracy
- experiment results
- research findings

Every reported result must come from actual generated data and actual calculations.

If an algorithm fails to recover a planted structure, report the failure honestly.

Do not modify the dataset after seeing results in order to make the experiment look better.

Do not manufacture research conclusions.

Clearly distinguish:

- generated ground truth
- measured result
- interpretation
- limitation

---

# 7. REPRODUCIBILITY

Every generated dataset and experiment must record enough metadata to reproduce it.

At minimum include:

- seed
- configuration
- dataset version
- generator version
- network size
- edge count
- time range
- weight mode
- experiment parameters
- generation timestamp

Save configuration alongside results.

Use deterministic random number generation.

Avoid hidden randomness.

---

# 8. IMPLEMENTATION ORDER

Follow this broad order unless the specifications require a justified change:

PHASE 0
Project initialization

PHASE 1
Organization generator

PHASE 2
Synthetic supply-chain network generator

PHASE 3
Transaction generator

PHASE 4
Temporal generation

PHASE 5
Data validation

PHASE 6
Graph builder

PHASE 7
Basic network statistics

PHASE 8
Centrality engine

PHASE 9
Centrality comparison

PHASE 10
Community detection

PHASE 11
K-core analysis

PHASE 12
Hidden dependency analysis

PHASE 13
Temporal SNA

PHASE 14
Resilience engine

PHASE 15
Ground-truth experiments

PHASE 16
Experiment runner

PHASE 17
Visualization engine

PHASE 18
Interactive dashboard

PHASE 19
Decentralized transaction abstraction

PHASE 20
Testing and integration

PHASE 21
Performance validation

PHASE 22
Research output generation

PHASE 23
Documentation

PHASE 24
Final research validation

The detailed requirements for these phases are defined in `CLAUDE_BUILD_PROMPT.md`.

---

# 9. PROJECT ARCHITECTURE

Target architecture:

    CONFIGURATION
          |
          v
    SYNTHETIC GENERATOR
          |
          v
    TRANSACTION DATASET
          |
          v
    GRAPH BUILDER
          |
       +--+--+
       |     |
       v     v
    STATIC  TEMPORAL
      SNA      SNA
       |       |
       +---+---+
           |
           v
    EXPERIMENT ENGINE
           |
           v
    RESULTS STORE
           |
           v
    VISUALIZATION
           |
           v
    STREAMLIT DASHBOARD

Optional later:

    TRANSACTION
         |
         v
    VALIDATION
         |
         v
    TRANSACTION STORE
         |
         v
    GRAPH BUILDER

The SNA engine must not depend on the decentralized backend.

---

# 10. INITIAL DEVELOPMENT DATASET

Do not begin with the largest possible dataset.

First create a small smoke-test configuration.

Example:

- 100 organizations
- 500 approximate edges
- 3 months

Use this to validate the complete pipeline quickly.

Then use the normal development configuration:

- 1,000 organizations
- approximately 5,000 edges
- 24 months

Then performance-test:

- 5,000 organizations
- approximately 25,000 edges

Then:

- 10,000 organizations
- 50,000+ edges

Do not optimize prematurely.

---

# 11. SYNTHETIC DATA REQUIREMENTS

The network must contain realistic structural patterns rather than a uniformly random graph.

Include:

- suppliers
- manufacturers
- distributors
- warehouses
- logistics providers
- retailers

Include planted:

- communities
- hubs
- bridge nodes
- dependency groups
- critical suppliers where specified

Use ground-truth metadata.

The generator should produce realistic:

- hierarchy
- regional structure
- business relationships
- degree heterogeneity
- relationship strengths
- temporal behavior
- disruptions

---

# 12. GRAPH REQUIREMENTS

Primary representation:

`networkx.DiGraph`

Support weighted edges.

Possible edge attributes:

- transaction_count
- total_quantity
- total_value
- average_lead_time
- relationship_type
- weight

Support weight modes:

- frequency
- quantity
- transaction_value

Document exactly what each means.

Do not silently mix weight semantics.

---

# 13. SNA REQUIREMENTS

Implement, where mathematically meaningful:

- in-degree
- out-degree
- total degree
- betweenness
- closeness
- eigenvector centrality
- PageRank
- k-core
- connected components
- clustering where appropriate
- path metrics where assumptions hold
- efficiency
- modularity
- community detection

Handle:

- directed graphs
- weighted graphs
- disconnected graphs
- convergence failures

Do not blindly calculate metrics where assumptions are violated.

Document methodological choices.

---

# 14. COMMUNITY DETECTION

Implement Louvain as the primary community method unless the specification requires otherwise.

Optionally support:

- Leiden
- greedy modularity

Calculate:

- community count
- community sizes
- modularity
- inter-community connectivity

Where planted community labels exist, evaluate recovery using appropriate metrics such as:

- Adjusted Rand Index
- Normalized Mutual Information

Do not compare detected communities to ground truth when ground truth is not defined.

---

# 15. DEPENDENCY ANALYSIS

Define dependency metrics explicitly.

Potential signals include:

- upstream concentration
- single-source dependency
- common upstream ancestor
- bridge relationships
- concentrated transaction weights

Example:

    supplier_dependency_ratio =
        quantity_from_supplier / total_quantity

Do not label an organization a "risk" without a defined measurable rule.

Use careful language such as:

- dependency concentration
- structural dependency
- upstream concentration

unless the methodology explicitly defines a risk metric.

---

# 16. TEMPORAL SNA

Generate multiple snapshots.

Default:

24 months.

Support:

1
6
12
24
36 months

Model events such as:

- organization entry
- organization inactivity
- relationship creation
- relationship weakening
- relationship strengthening
- seasonality
- disruption

Track:

- node count
- edge count
- density
- components
- centrality
- communities
- community persistence
- inter-community connectivity

---

# 17. RESILIENCE EXPERIMENTS

Implement:

1. random node removal
2. highest-degree removal
3. highest-betweenness removal
4. highest-PageRank removal

For random removal:

- multiple seeds
- multiple repetitions
- mean
- standard deviation
- confidence intervals if practical

Measure:

- largest component fraction
- network efficiency
- component count
- reachability

Do not use a single random run as a statistically meaningful comparison.

---

# 18. GROUND-TRUTH EXPERIMENTS

Run:

A. planted hub recovery

B. planted bridge recovery

C. planted community recovery

D. planted dependency recovery

E. planted critical-node resilience experiment

Use quantitative evaluation.

Save results in machine-readable formats.

---

# 19. DASHBOARD

Use Streamlit unless a strong technical reason exists to use another framework.

Create:

- Overview
- Network Explorer
- Centrality
- Communities
- Dependencies
- Temporal Analysis
- Resilience

Use actual calculated data.

Support filters for:

- time
- region
- organization type
- product
- community

Avoid rendering thousands of nodes simultaneously when that makes the dashboard unusable.

Use sensible sampling/filtering while preserving the underlying analytical data.

---

# 20. VISUALIZATION

Generate reusable plots for:

1. network
2. degree distribution
3. centrality comparison
4. centrality rankings
5. community graph
6. community size
7. temporal network metrics
8. temporal centrality
9. resilience curves
10. dependency graph

Save:

- PNG
- SVG where appropriate

Never hard-code analytical values.

---

# 21. DECENTRALIZED LAYER

Only build the decentralized layer after the SNA pipeline works.

Create an abstraction similar to:

    class TransactionStore:
        write_transaction(...)
        read_transactions(...)
        verify_transaction(...)

Implement at minimum:

    SyntheticTransactionStore

Optionally implement a placeholder/modular:

    BlockchainTransactionStore

Do not require Hyperledger, Ethereum, or another blockchain to run the SNA project.

If real blockchain infrastructure would significantly increase build complexity without improving the research objective, implement the abstraction and document the integration point rather than blocking the project.

---

# 22. TESTING STRATEGY

Create:

- unit tests
- integration tests
- reproducibility tests
- data validation tests
- graph tests
- SNA tests
- experiment tests

At minimum verify:

DATA:
- required schema
- unique IDs
- reproducibility
- valid values
- validation behavior

GRAPH:
- direction
- weights
- attributes
- temporal snapshots

SNA:
- centrality outputs
- community outputs
- k-core
- network statistics

EXPERIMENTS:
- resilience
- random seeds
- ground truth

INTEGRATION:

    generation
        ↓
    graph
        ↓
    SNA
        ↓
    experiments
        ↓
    reports

---

# 23. SMOKE TEST

Create an automated smoke test that runs the smallest meaningful end-to-end pipeline.

It should:

1. generate a small dataset
2. validate it
3. build a graph
4. run SNA
5. run one experiment
6. generate a result
7. verify expected output files exist

This should execute quickly.

Prefer a command such as:

`python -m tests.smoke_test`

or an equivalent pytest integration test.

---

# 24. FULL ACCEPTANCE TEST

Before completion, execute the real workflow.

At minimum:

    pip install -r requirements.txt

    python -m generator.generate --config config/default.yaml

    python -m graph.build

    python -m experiments.run --experiment all

    python -m reports.generate

    pytest

Verify that the dashboard can start:

    streamlit run dashboard/app.py

If launching a persistent Streamlit process is inconvenient, perform a startup/import smoke test and document how it was verified.

Inspect:

- generated dataset
- metadata
- graph
- SNA results
- experiment results
- figures
- tables
- summary
- dashboard data

---

# 25. RESEARCH REPORT

Generate a machine-derived research summary.

It must contain actual results from the experiment output.

Include:

- dataset statistics
- network statistics
- centrality findings
- community results
- dependency results
- temporal findings
- resilience findings
- ground-truth evaluation
- limitations

Do not invent unsupported conclusions.

---

# 26. DOCUMENTATION

Create or update:

`README.md`

`docs/architecture.md`

`docs/dataset.md`

`docs/methodology.md`

`docs/experiments.md`

`docs/dashboard.md`

`docs/limitations.md`

Explain:

- node definitions
- edge definitions
- graph direction
- edge weights
- centrality methodology
- community methodology
- dependency definitions
- temporal methodology
- resilience methodology
- synthetic-data assumptions
- limitations

---

# 27. CODE QUALITY

Use:

- Python type hints
- docstrings
- modular functions
- structured logging
- configuration files
- clear naming
- error handling
- small testable components

Avoid:

- giant scripts
- hidden global state
- hard-coded paths
- hard-coded results
- notebook-only implementation

Notebooks may be used for exploration only.

Production functionality must live in Python modules.

---

# 28. FAILURE RECOVERY

If Antigravity or Claude loses context:

1. Read `BUILD_PROGRESS.md`.
2. Inspect the repository.
3. Run the current smoke/integration tests.
4. Determine the last verified phase.
5. Continue from the first incomplete phase.
6. Do not rebuild working components unnecessarily.

If dependencies fail:

- diagnose the package/version problem
- choose a compatible version
- update requirements
- rerun installation/tests

If an algorithm becomes too slow:

1. profile
2. identify bottleneck
3. reduce unnecessary repeated computation
4. consider caching
5. consider igraph only if justified
6. document the decision

Do not replace correct algorithms with approximate methods solely to make the demo faster without documenting the change.

---

# 29. SECURITY AND DATA INTEGRITY

Even though data is synthetic:

- validate schemas
- validate imported data
- avoid arbitrary code execution
- sanitize uploaded data if import functionality exists
- keep analysis server-side
- do not trust client-side calculations as authoritative

---

# 30. FINAL QUALITY GATE

Do not declare the project complete until all applicable items below have been verified:

[ ] Repository structure exists

[ ] Dependencies install

[ ] Configuration loads

[ ] Synthetic organizations generate

[ ] Synthetic transactions generate

[ ] Ground truth is saved

[ ] Temporal data generates

[ ] Data validation runs

[ ] Graph construction works

[ ] Network statistics work

[ ] Centrality engine works

[ ] Community detection works

[ ] K-core works

[ ] Dependency analysis works

[ ] Temporal SNA works

[ ] Resilience experiments work

[ ] Ground-truth experiments work

[ ] Experiment runner works

[ ] Visualizations generate

[ ] Dashboard starts

[ ] Research outputs generate

[ ] Tests pass

[ ] Smoke test passes

[ ] Documentation exists

[ ] Reproducibility metadata exists

[ ] No analytical result is hard-coded

[ ] No unsupported research conclusion is generated

[ ] SNA works independently of blockchain

---

# 31. FINAL REPORT

When the project is actually complete, produce a concise final report containing:

## Status

Complete / Partial / Blocked

## Implemented

List major components.

## Files

List important created/modified files.

## Tests

Report actual commands and results.

## Dataset

Report actual generated size.

## Network

Report actual node/edge statistics.

## SNA

Report implemented analyses.

## Experiments

Report executed experiments.

## Dashboard

Report startup/verification status.

## Research Outputs

Report generated figures/tables/results.

## Known Limitations

Only real limitations.

## How To Run

Give the exact commands required for a clean user run.

## Important Decisions

List important architectural/methodological decisions.

Do not say "works" if it was not executed.

---

# 32. FINAL COMMAND CHECK

Before final response, verify the project can be started by a new developer using the README.

The final user workflow should be approximately:

    git clone <repository>

    cd supply-chain-sna

    python -m venv .venv

    # activate environment

    pip install -r requirements.txt

    python -m generator.generate --config config/default.yaml

    python -m graph.build

    python -m experiments.run --experiment all

    python -m reports.generate

    streamlit run dashboard/app.py

    pytest

If the actual commands differ, update README.md and report the actual commands.

---

# 33. FINAL INSTRUCTION

BEGIN NOW.

Do not provide a long plan and wait.

Inspect the repository and specification files first.

Create BUILD_PROGRESS.md.

Then execute the project phase-by-phase autonomously.

Keep moving until the complete system has been implemented, executed, tested, debugged, and documented.

The objective is not to produce a large amount of code.

The objective is to produce a WORKING, REPRODUCIBLE, RESEARCH-GRADE SNA PROJECT.
