# CLAUDE_BUILD_PROMPT.md
# Decentralized Supply Chain Social Network Analysis
## Phase-by-Phase Implementation Instructions for Claude

You are the primary software engineer responsible for implementing this project.

The complete project specification is provided separately in:
`decentralized_supply_chain_sna_project_spec.md`

You MUST treat that specification as the source of truth for project scope.

---

# 0. PRIMARY OBJECTIVE

Build a research-grade, reproducible Social Network Analysis system for a synthetic supply-chain network.

The project is primarily an **SNA project**.

The decentralized/blockchain layer is supporting infrastructure only.

The final system must answer:

1. Which organizations are structurally important?
2. Which organizations act as bottlenecks or bridges?
3. What hidden dependencies exist?
4. What communities exist?
5. How does the network evolve over time?
6. How resilient is the network to targeted and random failures?
7. Can SNA algorithms recover known structural patterns planted into the synthetic dataset?

The final output must be an interactive analytics dashboard plus reproducible experiments and exported research results.

---

# 1. NON-NEGOTIABLE PRINCIPLES

## 1.1 SNA comes first

Do NOT turn this into a blockchain project.

Priority order:

1. Synthetic network generation
2. Graph modeling
3. SNA
4. Experiments
5. Visualization
6. Research outputs
7. Decentralized transaction layer

The SNA system must work independently of the blockchain layer.

---

## 1.2 No fake results

Never hard-code:

- Centrality values
- Community counts
- Resilience percentages
- Rankings
- Research findings
- Accuracy metrics

Every reported result must be calculated from the generated dataset.

---

## 1.3 Reproducibility

Every experiment must be reproducible using:

- Configuration files
- Explicit random seeds
- Versioned parameters
- Saved datasets
- Saved experiment metadata

A researcher should be able to regenerate the same experiment.

---

## 1.4 Synthetic data must be realistic

Do NOT generate a purely random graph.

The generator must intentionally model realistic supply-chain structure:

- Hierarchical flow
- Hubs
- Communities
- Bridges
- Dependencies
- Heterogeneous node degree
- Temporal evolution
- Failures/disruptions

---

## 1.5 Ground truth is mandatory

Because the dataset is synthetic, the generator should know certain hidden truths.

Examples:

```text
planted_bridge_nodes
planted_critical_suppliers
planted_communities
planted_dependency_groups
```

The SNA system should then attempt to discover these structures.

This allows quantitative evaluation.

---

# 2. EXPECTED TECHNOLOGY STACK

Use Python as the primary language.

Recommended:

- Python 3.11+
- Pandas
- NumPy
- NetworkX
- SciPy where needed
- Faker
- Plotly
- Streamlit
- PyYAML
- pytest

Optional:

- python-louvain if required
- igraph for performance benchmarking
- PostgreSQL
- Neo4j

Do not introduce unnecessary dependencies.

The blockchain component can be implemented later and should remain modular.

---

# 3. TARGET ARCHITECTURE

Implement:

```text
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
             +-----------+-----------+
             |                       |
             v                       v
       STATIC SNA                TEMPORAL SNA
             |                       |
             +-----------+-----------+
                         |
                         v
                 EXPERIMENT ENGINE
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
        Centrality   Community   Resilience
                         |
                         v
                  RESULTS STORE
                         |
                         v
                 VISUALIZATION API
                         |
                         v
                   STREAMLIT UI
```

Later:

```text
Synthetic Transactions
        |
        v
Decentralized Ledger
        |
        v
Verified Transactions
        |
        v
Graph Builder
```

---

# 4. DEVELOPMENT RULE

Implement one phase at a time.

After every phase:

1. Run tests.
2. Run a small example.
3. Verify output.
4. Document what was implemented.
5. Do not proceed if the phase is broken.

Do not create a huge amount of code before testing.

---

# PHASE 0 — PROJECT INITIALIZATION

## Goal

Create a clean, maintainable repository.

Create:

```text
supply-chain-sna/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
├── data/
├── generator/
├── graph/
├── sna/
├── experiments/
├── dashboard/
├── tests/
├── notebooks/
├── reports/
└── docs/
```

Create a configuration system.

Example:

```yaml
seed: 42

network:
  organizations: 1000
  months: 24

organization_types:
  suppliers: 0.30
  manufacturers: 0.15
  distributors: 0.20
  warehouses: 0.10
  logistics: 0.10
  retailers: 0.15
```

Make parameters configurable.

### Acceptance criteria

- Project runs.
- Environment installs successfully.
- Configuration loads.
- A basic pytest test passes.

---

# PHASE 1 — ORGANIZATION GENERATOR

## Goal

Generate realistic supply-chain organizations.

Each organization should contain:

```text
organization_id
organization_name
organization_type
region
industry
size_category
status
created_at
```

Organization types:

- Supplier
- Manufacturer
- Distributor
- Warehouse
- Logistics Provider
- Retailer

Generate realistic names.

Use deterministic Faker/random seeds.

Example:

```text
SUP-00001
MFG-00015
DST-00231
RET-00891
```

Do not use random strings that are impossible to interpret.

### Requirements

- Configurable number of organizations
- Configurable organization-type distribution
- Multiple regions
- Multiple industries
- Stable IDs
- Reproducible generation

### Tests

Verify:

- IDs are unique
- Organization types are valid
- Required columns exist
- Seed produces identical output

---

# PHASE 2 — SYNTHETIC NETWORK GENERATOR

## Goal

Generate realistic relationships.

Do NOT connect nodes uniformly at random.

Implement supply-chain constraints:

```text
Supplier → Manufacturer
Manufacturer → Distributor
Distributor → Retailer
Manufacturer → Warehouse
Warehouse → Distributor
Logistics → Organizations
```

Allow realistic exceptions where appropriate.

---

# 2.1 Communities

Create regional/business communities.

Example:

```text
Region A
  Supplier → Manufacturer → Distributor → Retailer

Region B
  Supplier → Manufacturer → Distributor → Retailer
```

Store the planted community:

```python
ground_truth["communities"]
```

---

# 2.2 Hubs

Create selected organizations with unusually high connectivity.

Store:

```python
ground_truth["hub_nodes"]
```

---

# 2.3 Bridge nodes

Create organizations connecting otherwise separated communities.

Store:

```python
ground_truth["bridge_nodes"]
```

---

# 2.4 Hidden dependencies

Create scenarios where multiple organizations indirectly depend on the same upstream organization.

Example:

```text
S1 ─┐
S2 ─┼──> U
S3 ─┘
     |
     v
   M1/M2/M3
```

Store:

```python
ground_truth["dependency_groups"]
```

---

# 2.5 Degree heterogeneity

Realistic networks should not have every node with approximately the same number of connections.

Implement configurable heterogeneity.

Do not blindly assume a particular statistical distribution unless justified.

---

# PHASE 3 — TRANSACTION GENERATOR

Generate transaction-level data.

Schema:

```text
transaction_id
timestamp
source_node
target_node
product_id
product_category
quantity
unit
transaction_value
region
relationship_type
lead_time_days
status
```

Requirements:

- Directed transactions
- Multiple products
- Different quantities
- Different values
- Different relationship strengths
- Temporal timestamps

Transactions should aggregate into edges.

---

# PHASE 4 — TEMPORAL GENERATION

Generate multiple time periods.

Default:

```text
24 months
```

Support:

```text
1 month
6 months
12 months
24 months
36 months
```

Implement events:

- New organization enters
- Organization becomes inactive
- New relationship appears
- Relationship weakens
- Relationship strengthens
- Seasonal demand
- Disruption

Save an event log.

Example:

```text
event_id
timestamp
event_type
organization_id
target_id
severity
description
```

---

# PHASE 5 — DATA VALIDATION

Before graph construction, implement a validation layer.

Check:

- Duplicate transaction IDs
- Missing nodes
- Invalid organization types
- Invalid timestamps
- Negative quantities
- Invalid edges
- Orphan nodes
- Duplicate records

Produce:

```text
data_quality_report.json
```

Do not silently repair major problems.

---

# PHASE 6 — GRAPH BUILDER

Convert transaction data into graph representations.

Primary graph:

```python
nx.DiGraph()
```

Weighted graph:

```python
nx.DiGraph()
```

with edge attributes such as:

```text
transaction_count
total_quantity
total_value
average_lead_time
```

Support different weight modes:

```text
frequency
quantity
transaction_value
```

Document exactly what each means.

---

# 6.1 Node attributes

Attach:

```text
organization_type
region
industry
size_category
status
```

---

# 6.2 Edge attributes

Attach:

```text
weight
transaction_count
total_quantity
total_value
relationship_type
```

---

# 6.3 Temporal graph

Create snapshots:

```text
2026-01
2026-02
...
```

Do not mix temporal records incorrectly.

---

# PHASE 7 — BASIC NETWORK STATISTICS

Implement:

- Number of nodes
- Number of edges
- Density
- Average degree
- Degree distribution
- Connected components
- Largest connected component
- Average clustering where meaningful
- Average path length where meaningful
- Modularity where applicable
- Network efficiency

For directed graphs, explicitly document how each metric is computed.

Do not calculate a metric when its assumptions are violated.

---

# PHASE 8 — CENTRALITY ENGINE

Implement separately:

```text
degree.py
betweenness.py
closeness.py
eigenvector.py
pagerank.py
```

Each function should:

- Accept graph
- Return structured result
- Preserve node ID
- Support configurable parameters
- Handle errors cleanly

---

# 8.1 Degree

Return:

```text
node
in_degree
out_degree
total_degree
```

---

# 8.2 Betweenness

Return:

```text
node
betweenness
```

Use normalized values where appropriate.

---

# 8.3 Closeness

Handle disconnected graphs appropriately.

Document the chosen NetworkX formulation.

---

# 8.4 Eigenvector

Handle convergence failures.

Expose:

```text
max_iter
tol
```

---

# 8.5 PageRank

Expose:

```text
alpha
max_iter
tol
```

---

# PHASE 9 — CENTRALITY COMPARISON

Create a combined table:

```text
node
degree
betweenness
closeness
eigenvector
pagerank
```

Generate:

- Top-N table
- Rank correlations
- Rank differences

Useful analysis:

```text
Which nodes rank highly under multiple metrics?
Which nodes are highly connected but low-betweenness?
Which nodes are bridges despite moderate degree?
```

Do not collapse everything into one arbitrary score unless explicitly justified.

---

# PHASE 10 — COMMUNITY DETECTION

Implement:

- Louvain

Optionally:

- Leiden
- Greedy modularity

Return:

```text
node
community_id
```

Calculate:

- Number of communities
- Community sizes
- Modularity
- Inter-community edges

---

# 10.1 Ground-truth evaluation

Compare detected communities against planted communities.

Possible metrics:

- Adjusted Rand Index
- Normalized Mutual Information

Only use these where ground truth exists.

---

# PHASE 11 — K-CORE ANALYSIS

Implement k-core decomposition.

Output:

```text
node
core_number
```

Visualize:

- Core vs peripheral nodes
- Core size
- Core organization types

Interpret carefully.

k-core membership does not automatically mean "business importance."

---

# PHASE 12 — HIDDEN DEPENDENCY ANALYSIS

Implement structural dependency detection.

Potential signals:

- High upstream concentration
- Single-source dependencies
- Common upstream ancestor
- Bridge relationships
- Concentrated edge weights

Make every definition explicit.

For example:

```text
supplier_dependency_ratio =
quantity_from_supplier / total_quantity
```

Do not label something a "risk" unless a defined rule supports it.

---

# PHASE 13 — TEMPORAL SNA

For each time period:

Calculate:

```text
nodes
edges
density
components
centrality
communities
```

Track node-level centrality through time.

Example output:

```text
timestamp
node
degree
betweenness
pagerank
community
```

Generate temporal plots.

---

# 13.1 Community evolution

Track:

- Community size
- Community membership
- Community persistence
- Inter-community connectivity

If implementing community matching across time, document the matching algorithm.

---

# PHASE 14 — RESILIENCE ENGINE

Implement controlled node-removal experiments.

## Strategy 1

Random removal.

Repeat multiple times.

Report mean and variance.

## Strategy 2

Highest-degree removal.

## Strategy 3

Highest-betweenness removal.

## Strategy 4

Highest-PageRank removal.

For each:

```text
fraction_removed
largest_component_fraction
network_efficiency
component_count
reachability
```

---

# 14.1 Important experimental rule

Do not compare only one random failure run against one targeted run.

For random failure:

- Run multiple seeds
- Calculate mean
- Calculate standard deviation
- Optionally show confidence intervals

This prevents misleading results.

---

# PHASE 15 — GROUND-TRUTH EXPERIMENTS

Use synthetic planted structures.

## Experiment A

Can centrality identify planted hubs?

## Experiment B

Can betweenness identify planted bridges?

## Experiment C

Can community detection recover planted communities?

## Experiment D

Can dependency analysis identify planted dependency groups?

## Experiment E

Does removing planted critical nodes produce measurable network degradation?

Store results in machine-readable files.

---

# PHASE 16 — EXPERIMENT RUNNER

Create a unified CLI.

Example:

```bash
python -m experiments.run --config config/default.yaml
```

Support:

```bash
--experiment centrality
--experiment communities
--experiment resilience
--experiment temporal
--experiment all
```

Generate:

```text
reports/results/
├── centrality.csv
├── communities.csv
├── resilience.csv
├── temporal.csv
└── summary.json
```

---

# PHASE 17 — VISUALIZATION ENGINE

Create reusable plotting functions.

Required plots:

1. Network graph
2. Degree distribution
3. Centrality comparison
4. Centrality ranking
5. Community graph
6. Community size distribution
7. Temporal network metrics
8. Temporal centrality
9. Resilience curves
10. Dependency graph

Save:

- PNG
- SVG where appropriate

Never hard-code values.

---

# PHASE 18 — INTERACTIVE DASHBOARD

Use Streamlit unless another framework is justified.

Dashboard:

```text
Overview
Network Explorer
Centrality
Communities
Dependencies
Temporal Analysis
Resilience
```

---

# 18.1 Overview

Show:

- Nodes
- Edges
- Density
- Components
- Communities
- Current time period

---

# 18.2 Network Explorer

Filters:

- Time
- Region
- Organization type
- Product
- Community

Node click/details:

```text
Organization
Type
Region
Degree
Betweenness
Closeness
Eigenvector
PageRank
Community
Core number
```

---

# 18.3 Centrality

Show:

- Top-N organizations
- Metric comparison
- Rank correlation
- Distribution

---

# 18.4 Communities

Show:

- Community graph
- Community size
- Modularity
- Community composition

---

# 18.5 Dependencies

Show:

- Dependency concentration
- Bridge nodes
- Upstream/downstream relationships
- Defined dependency metrics

---

# 18.6 Temporal

Allow selecting:

```text
Start date
End date
```

Show:

- Network evolution
- Centrality evolution
- Community evolution

---

# 18.7 Resilience

Controls:

```text
Attack strategy
Number/fraction of nodes removed
Random seed
```

Show:

- Largest component
- Efficiency
- Components
- Degradation curve

---

# PHASE 19 — DECENTRALIZED LAYER

Only implement after SNA works.

The decentralized layer must be modular.

Minimum conceptual flow:

```text
Transaction
   ↓
Validation
   ↓
Ledger
   ↓
Retrieval
   ↓
Graph Builder
```

Possible implementation:

- Hyperledger Fabric
- Private Ethereum-compatible network

For the academic prototype, a permissioned architecture is acceptable.

Do not spend most development time on blockchain.

---

# 19.1 Blockchain abstraction

Create an interface:

```python
class TransactionStore:
    def write_transaction(...)
    def read_transactions(...)
    def verify_transaction(...)
```

Then implement:

```text
SyntheticTransactionStore
BlockchainTransactionStore
```

The SNA engine should not care which backend supplied the transactions.

This allows development/testing without the blockchain running.

---

# PHASE 20 — TESTING

Write tests for:

### Data

- Generator
- Schema
- Reproducibility
- Validation

### Graph

- Direction
- Weights
- Attributes
- Temporal snapshots

### SNA

- Centrality correctness
- Community output
- k-core
- Network metrics

### Experiments

- Resilience
- Ground truth
- Random seeds

### Dashboard

At minimum test backend/data functions independently of the UI.

---

# PHASE 21 — PERFORMANCE

Start with:

```text
1,000 nodes
5,000 edges
```

Then test:

```text
5,000 nodes
25,000 edges
```

Then:

```text
10,000 nodes
50,000+ edges
```

Record runtime and memory where practical.

Do not optimize prematurely.

If NetworkX becomes a bottleneck:

1. Profile.
2. Identify the expensive algorithm.
3. Consider igraph or another implementation.
4. Document the reason.

---

# PHASE 22 — RESEARCH OUTPUT GENERATION

Create a command:

```bash
python -m reports.generate
```

It should generate:

```text
reports/
├── figures/
├── tables/
├── results/
└── summary.md
```

The summary must be generated from actual experiment outputs.

It should include:

- Dataset statistics
- Network statistics
- Top centrality findings
- Community results
- Dependency findings
- Resilience findings
- Temporal findings
- Ground-truth evaluation

Do not generate unsupported interpretations.

---

# PHASE 23 — DOCUMENTATION

Create:

```text
docs/
├── architecture.md
├── dataset.md
├── methodology.md
├── experiments.md
├── dashboard.md
└── limitations.md
```

Documentation should explain:

- Why each SNA metric is used
- How the synthetic data is generated
- What each graph represents
- How weights are defined
- How temporal snapshots work
- How resilience is measured
- What limitations exist

---

# PHASE 24 — FINAL RESEARCH CHECK

Before declaring completion, verify that the project can answer:

### Structural importance

Who is structurally important?

### Intermediation

Who bridges different parts of the network?

### Communities

What groups exist?

### Dependency

Where is supply concentrated?

### Temporal change

How does the network evolve?

### Resilience

What happens when important nodes fail?

### Validation

Can the algorithms recover planted structures?

---

# 25. RUBRIC ALIGNMENT

The implementation must support these research deliverables:

## Introduction & Context

Provide:

- Clear research problem
- Background
- SNA relevance
- Research questions

## Network Data Collection & Sources

Provide:

- Synthetic dataset justification
- Generation methodology
- Schema
- Assumptions
- Limitations

## Network Modeling & Methodology

Provide:

- Node/edge definitions
- Directed/weighted justification
- Centrality
- Clustering/community detection
- Resilience methodology
- Temporal SNA

## Analysis & Interpretation

Provide:

- Actual experimental findings
- Network metrics
- Community interpretation
- Dependency interpretation
- Resilience interpretation

## Visualization

Provide:

- Network graphs
- Community graphs
- Centrality plots
- Temporal plots
- Resilience curves

## Discussion & Implications

Provide:

- Real-world interpretation
- Potential applications
- Limitations
- Future research

## Conclusion

Provide:

- Research question answers
- Main findings
- Contribution

---

# 26. WHAT NOT TO DO

Do NOT:

- Build only a blockchain explorer.
- Generate a random Erdős–Rényi graph and call it a supply chain.
- Hard-code centrality rankings.
- Invent research conclusions.
- Treat degree as universal importance.
- Call every highly connected node a "risk."
- Claim that SNA proves causality.
- Add machine learning just because it sounds impressive.
- Add a graph database unless necessary.
- Build cryptocurrency/token functionality.
- Depend on blockchain for the SNA engine to function.
- Hide synthetic-data assumptions.
- Use visualizations that do not support an analytical question.
- Produce only screenshots without numerical results.
- Use a single random resilience simulation and call it statistically meaningful.

---

# 27. CODING QUALITY REQUIREMENTS

Use:

- Type hints
- Docstrings
- Modular functions
- Clear naming
- Small testable components
- Structured logging
- Configuration files
- Error handling

Avoid:

- Giant scripts
- Global state
- Hard-coded paths
- Hard-coded experiment results
- Notebook-only implementation

Notebooks may be used for exploration, but the production implementation must be Python modules.

---

# 28. CLI REQUIREMENTS

Provide commands similar to:

```bash
python -m generator.generate
python -m graph.build
python -m sna.analyze
python -m experiments.run --experiment all
streamlit run dashboard/app.py
python -m reports.generate
```

Support:

```bash
--config
--seed
--output
```

where appropriate.

---

# 29. REPRODUCIBILITY REQUIREMENTS

Every experiment should record:

```json
{
  "seed": 42,
  "dataset_version": "v1",
  "network_size": 5000,
  "edge_count": 25000,
  "weight_mode": "quantity",
  "timestamp": "..."
}
```

Save configuration alongside results.

---

# 30. DATA VERSIONING

Every generated dataset should have metadata:

```text
dataset_id
seed
generation_timestamp
generator_version
configuration
node_count
edge_count
time_range
scenario
```

This makes the research reproducible.

---

# 31. SECURITY / DATA INTEGRITY

Even though the data is synthetic:

- Validate input
- Validate transaction schemas
- Do not trust client-side dashboard calculations
- Keep analysis server-side
- Avoid arbitrary code execution
- Sanitize uploaded/imported data if import functionality is added

---

# 32. FINAL ACCEPTANCE TEST

A clean environment should be able to execute:

```bash
pip install -r requirements.txt
```

Then:

```bash
python -m generator.generate --config config/default.yaml
```

Then:

```bash
python -m graph.build
```

Then:

```bash
python -m experiments.run --experiment all
```

Then:

```bash
streamlit run dashboard/app.py
```

The dashboard must display actual generated data.

Then:

```bash
python -m reports.generate
```

must generate the research figures/tables/results.

---

# 33. FINAL EXPECTED OUTPUT

The completed repository should contain:

```text
1. Synthetic supply-chain dataset
2. Ground-truth metadata
3. Graph construction engine
4. SNA engine
5. Centrality analysis
6. Community detection
7. k-core analysis
8. Dependency analysis
9. Temporal SNA
10. Resilience simulation
11. Ground-truth evaluation
12. Interactive dashboard
13. Decentralized transaction layer
14. Automated experiments
15. Figures
16. Tables
17. Research summaries
18. Tests
19. Documentation
20. Reproducible configuration
```

---

# 34. FINAL RESEARCH NARRATIVE

The implementation should ultimately support this research narrative:

```text
Supply-chain organizations
        ↓
Business relationships
        ↓
Directed weighted network
        ↓
Social Network Analysis
        ↓
Who is important?
        ↓
Who is a bridge?
        ↓
Where are communities?
        ↓
Where are dependencies?
        ↓
How does the network evolve?
        ↓
What happens when nodes fail?
        ↓
What structural insights can be extracted?
```

The decentralized layer supports:

```text
Are the underlying transactions
recorded in a trusted/shared way?
```

The project contribution remains:

> **Using Social Network Analysis to understand the structure, dependency, influence, evolution, and resilience of supply-chain networks.**

---

# 35. IMPLEMENTATION BEHAVIOR FOR CLAUDE

When implementing:

1. Read `decentralized_supply_chain_sna_project_spec.md`.
2. Read this file.
3. Inspect the current repository before changing anything.
4. Create a short implementation plan.
5. Implement only the current phase.
6. Run tests.
7. Run a real sample.
8. Inspect generated outputs.
9. Fix issues.
10. Document the phase.
11. Move to the next phase.

At every phase, report:

```text
PHASE:
IMPLEMENTED:
FILES CREATED/MODIFIED:
TESTS:
SAMPLE OUTPUT:
KNOWN LIMITATIONS:
NEXT PHASE:
```

Never claim a feature works without actually executing it.

If a design decision is ambiguous, choose the simplest academically defensible implementation and document the assumption.

If an algorithm has mathematical limitations on disconnected/directed/weighted graphs, explicitly handle or document them rather than silently producing misleading results.

The final implementation must prioritize **research correctness, reproducibility, explainability, and SNA depth** over unnecessary technical complexity.
