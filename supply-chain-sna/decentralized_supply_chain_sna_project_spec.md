# Decentralized Supply Chain Social Network Analysis
## FYP / Social Network Case Study — Complete Project Specification

> **Primary focus:** Social Network Analysis (SNA) of supply-chain relationships.  
> **Supporting component:** A decentralized/trusted transaction layer.  
> **Dataset:** Synthetic, but generated to represent realistic supply-chain structures and behaviors.

---

# 1. Project Title

**Social Network Analysis of Decentralized Supply Chain Networks for Dependency, Influence and Risk Identification**

Alternative shorter title:

**Decentralized Supply Chain Network Analytics Using Social Network Analysis**

---

# 2. Project Positioning

This is **primarily an SNA project**, not a blockchain project.

The central research contribution is to model a supply chain as a **dynamic, weighted, directed network** and use Social Network Analysis to identify:

- Structurally important organizations
- Highly connected organizations
- Critical intermediaries and bottlenecks
- Hidden dependencies
- Supply-chain communities
- Network fragmentation
- Structural vulnerabilities
- Changes in network structure over time
- Effects of simulated organization failures

A decentralized ledger/blockchain layer is a **supporting component** whose purpose is to provide a trusted and tamper-resistant source of transaction records.

The project should NOT become primarily about:

- Cryptocurrency
- Tokenization
- Complex smart contracts
- Generic blockchain development
- Basic product tracking
- A simple supply-chain dashboard

The SNA engine, analysis, interpretation, and visualizations are the heart of the project.

---

# 3. Research Problem

Traditional supply-chain systems generally represent relationships as operational transactions or linear flows. This can make it difficult to understand the **overall network structure** and identify organizations whose position in the network makes them particularly important.

The project investigates:

> **How can Social Network Analysis be used to identify influential organizations, critical intermediaries, hidden dependencies, communities, and structural vulnerabilities within a supply-chain network?**

A secondary question is:

> **Can a decentralized/trusted transaction layer provide a reliable foundation for constructing and analyzing the supply-chain network?**

---

# 4. Core Research Questions

## RQ1 — Structural Importance

Which organizations are structurally important within the supply-chain network?

Use:

- Degree Centrality
- Eigenvector Centrality
- PageRank

Do not assume that the organization with the most connections is automatically the most influential. Compare different centrality measures.

---

## RQ2 — Critical Intermediaries

Which organizations act as bottlenecks or bridges between otherwise separated parts of the supply chain?

Primary metric:

- Betweenness Centrality

Analyze what happens when highly intermediary nodes are removed.

---

## RQ3 — Hidden Dependencies

Can network structure reveal dependencies that are not obvious from individual transaction records?

Examples:

- Multiple suppliers ultimately depending on the same upstream source
- Multiple manufacturers depending on one critical supplier
- Several distributors depending on one intermediary
- Multiple network communities connected through a small number of bridge organizations

---

## RQ4 — Communities

What naturally occurring communities exist within the supply-chain network?

Use:

- Community detection
- Louvain or another appropriate community-detection algorithm

Investigate whether communities correspond to:

- Regions
- Supplier ecosystems
- Manufacturer ecosystems
- Logistics ecosystems
- Business clusters

Do not assume what communities represent before analyzing them.

---

## RQ5 — Network Resilience

How sensitive is the supply-chain network to the failure of structurally important organizations?

Simulate:

1. Random node removal
2. Highest-degree node removal
3. Highest-betweenness node removal
4. Highest-eigenvector/PageRank node removal

Compare the resulting network structure against the original network.

Measure:

- Connected components
- Largest connected component
- Average path length where meaningful
- Network efficiency
- Reachability
- Fragmentation

---

## RQ6 — Temporal Evolution

How does the supply-chain network evolve over time?

Analyze network snapshots across:

- Month
- Quarter
- Year

Track:

- Centrality changes
- New organizations
- Removed/inactive organizations
- Community changes
- Density changes
- Emerging bottlenecks
- Network fragmentation

This makes the project a **dynamic/temporal SNA study**, rather than only a static graph analysis.

---

# 5. Real-World Example

Consider a pharmaceutical supply chain:

```text
Supplier A ──────┐
                 │
Supplier B ──────┼──> Manufacturer X ───> Distributor D
                 │                            │
Supplier C ──────┘                            ▼
                                         Retailer R1

Supplier E ─────────────> Manufacturer Y ───> Distributor F
                                              │
                                              ▼
                                          Retailer R2
```

Each organization is a node.

Each business relationship/transaction is an edge.

Example transaction records:

| From | To | Product | Quantity | Date |
|---|---|---|---:|---|
| Supplier A | Manufacturer X | Chemical X | 500 kg | 2026-01-01 |
| Supplier B | Manufacturer X | Chemical X | 300 kg | 2026-01-02 |
| Supplier C | Manufacturer X | Chemical Y | 200 kg | 2026-01-03 |
| Manufacturer X | Distributor D | Medicine X | 10,000 | 2026-01-05 |
| Distributor D | Retailer R1 | Medicine X | 5,000 | 2026-01-07 |

The system transforms these transactions into a network.

---

# 6. What the System Should Determine

The final system should answer questions such as:

### Who is highly connected?

Degree Centrality.

### Who is structurally important because they connect to other important organizations?

Eigenvector Centrality / PageRank.

### Who acts as a bridge between communities?

Betweenness Centrality.

### Which organizations are embedded in tightly connected regions?

Community Detection / k-core analysis.

### Which organizations create major network disruption when removed?

Resilience simulation.

### How does the structure change over time?

Temporal SNA.

---

# 7. Synthetic Dataset Decision

## Yes — the primary dataset should be synthetic.

A synthetic dataset is appropriate for this project because real company-to-company supply-chain transaction data is difficult to obtain due to:

- Commercial confidentiality
- Privacy
- Incomplete supplier relationships
- Lack of detailed transaction-level public datasets
- Difficulty obtaining longitudinal relationship data

However, the synthetic dataset must **not be random noise**.

It should be a **realistic synthetic supply-chain network** generated according to documented rules.

The methodology must clearly state that the dataset is synthetic.

---

# 8. Synthetic Dataset Design

Generate a sufficiently large network so that SNA produces meaningful results.

Recommended initial scale:

- 1,000–5,000 organizations
- 5,000–50,000 relationships/transactions
- 12–36 monthly time periods
- Multiple organization types
- Multiple geographic regions
- Multiple products/categories

The exact size should be configurable.

Example:

```text
10,000 organizations
40,000 relationships
24 months
```

Start smaller during development, then scale up.

---

# 9. Organization Types

Each node should have attributes such as:

```text
organization_id
organization_name
organization_type
region
industry
size_category
status
```

Organization types:

- Supplier
- Manufacturer
- Distributor
- Warehouse
- Logistics Provider
- Retailer

Optionally:

- Raw Material Supplier
- Component Supplier
- Contract Manufacturer
- Regional Distributor

---

# 10. Transaction / Edge Schema

Recommended transaction schema:

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

For SNA, the important fields are:

```text
source_node
target_node
timestamp
quantity
transaction_value
```

---

# 11. Graph Representation

Represent the supply chain as a:

## Directed graph

```text
Supplier → Manufacturer → Distributor → Retailer
```

Direction matters because supply-chain relationships have direction.

---

## Weighted graph

Edge weight can represent:

- Transaction frequency
- Quantity
- Transaction value
- Relationship strength

The implementation should support multiple weighting schemes.

Example:

```text
A → B

weight = 5000 units
```

or:

```text
A → B

weight = ₹25,00,000 transaction value
```

Do not assume one weight is universally correct. Compare or document the selected definition.

---

# 12. Synthetic Network Generation

The generator should intentionally produce realistic network structures.

Do NOT simply generate:

```python
random_graph()
```

Instead, use rules such as:

### Supply-chain hierarchy

```text
Suppliers
    ↓
Manufacturers
    ↓
Distributors
    ↓
Retailers
```

### Heterogeneous connectivity

Some organizations should naturally have more relationships than others.

### Communities

Generate regional/business clusters.

### Hub organizations

Some organizations should become highly connected.

### Bridge organizations

Some organizations should connect otherwise separated communities.

### Dependencies

Create realistic cases where several downstream organizations depend on one upstream organization.

### Failures

Introduce some inactive/removed organizations during later time periods.

### Temporal changes

Allow:

- New companies
- Company exits
- New relationships
- Relationship weakening
- Relationship strengthening
- Seasonal demand
- Disruptions

This allows meaningful temporal SNA.

---

# 13. Controlled Ground Truth

One major advantage of synthetic data is that the generator can embed known structural patterns.

For example:

```text
Known critical supplier:
Supplier_001
```

or:

```text
Known bridge:
Distributor_050
```

or:

```text
Known community:
Region_A
```

The SNA algorithms then attempt to discover these patterns.

This creates a way to evaluate the methodology.

For example:

> Does betweenness centrality successfully identify intentionally created bridge organizations?

> Does community detection recover the planted communities?

This is much stronger than simply generating a graph and displaying metrics.

---

# 14. Synthetic Data Scenarios

Create multiple scenarios.

## Scenario A — Normal Network

Healthy supply chain.

## Scenario B — Single Critical Supplier

One supplier has unusually high structural importance.

## Scenario C — Hub-and-Spoke

Several organizations depend heavily on a central organization.

## Scenario D — Multiple Communities

Several relatively independent supply-chain clusters.

## Scenario E — Hidden Dependency

Several apparent suppliers ultimately depend on one upstream organization.

## Scenario F — Disruption

Remove one or more critical nodes.

## Scenario G — Community Disconnection

Remove bridge nodes between communities.

## Scenario H — Temporal Evolution

Organizations and relationships change over time.

These scenarios make the experiments reproducible.

---

# 15. SNA Methodology

## 15.1 Degree Centrality

Purpose:

Identify highly connected organizations.

For directed graphs, analyze:

- In-degree
- Out-degree
- Total degree

Interpretation must consider what the direction means.

Example:

High in-degree:

> Many organizations supply this organization.

High out-degree:

> This organization supplies many organizations.

---

# 16. Betweenness Centrality

Purpose:

Identify bridge/intermediary organizations.

Interpretation:

An organization with high betweenness lies on many shortest paths between other nodes.

Use this to investigate:

- Bottlenecks
- Bridge organizations
- Dependency concentration

---

# 17. Closeness Centrality

Purpose:

Identify organizations that are structurally close to many other organizations.

Useful for studying:

- Network accessibility
- Propagation
- Information/product reach

Be careful with disconnected graphs and use an appropriate formulation.

---

# 18. Eigenvector Centrality

Purpose:

Measure connections to important nodes.

An organization can have relatively few connections but still have high structural importance if its connections are themselves highly important.

---

# 19. PageRank

Use PageRank as another measure of structural importance in the directed network.

Compare it against other centrality measures rather than treating it as the single "importance score."

---

# 20. Community Detection

Use:

- Louvain initially
- Optionally compare with another method

Analyze:

- Number of communities
- Community sizes
- Modularity
- Inter-community edges
- Bridge nodes

---

# 21. k-Core Analysis

Use k-core decomposition to identify tightly embedded portions of the network.

This can reveal:

- Core organizations
- Peripheral organizations
- Highly interconnected supply-chain structures

---

# 22. Network-Level Metrics

Calculate:

- Number of nodes
- Number of edges
- Density
- Average degree
- Degree distribution
- Connected components
- Largest connected component
- Average clustering where meaningful
- Average path length where meaningful
- Modularity
- Network efficiency

For directed networks, clearly document which graph transformation or formulation is used for each metric.

---

# 23. Temporal SNA

Create network snapshots:

```text
2026-01
2026-02
2026-03
...
2027-12
```

For each snapshot calculate:

```text
nodes
edges
density
centrality
communities
components
```

Then track changes.

Example output:

```text
Company X

Jan: Betweenness = 0.21
Jun: Betweenness = 0.38
Dec: Betweenness = 0.61
```

This could indicate that Company X has become increasingly structurally important.

Do not claim causality merely from this change.

---

# 24. Resilience Analysis

Baseline:

```text
Original network
```

Then perform node-removal experiments.

### Random failure

Randomly remove nodes.

### Targeted degree attack

Remove highest-degree nodes.

### Targeted betweenness attack

Remove highest-betweenness nodes.

### Targeted PageRank/eigenvector attack

Remove structurally important nodes.

After each removal calculate:

```text
Largest Connected Component
Network Efficiency
Fragmentation
Reachability
Path Length
```

Plot the degradation curve.

Example:

```text
Nodes Removed (%)

0%    → 100% network efficiency
5%    → 88%
10%   → 70%
20%   → 45%
```

These values must come from the actual experiment, not be hard-coded.

---

# 25. Dashboard

Build an interactive SNA dashboard.

Suggested technology:

- Python backend
- NetworkX / igraph
- Pandas
- Plotly
- Streamlit or Dash

Optional:

- Cytoscape.js
- D3.js

---

# 26. Dashboard Pages

## Page 1 — Overview

Show:

- Total organizations
- Total relationships
- Network density
- Number of communities
- Connected components
- Time range

---

## Page 2 — Network Explorer

Interactive graph.

Filters:

- Organization type
- Region
- Product
- Time period
- Community

Clicking a node should show:

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
```

---

## Page 3 — Centrality Analysis

Charts for:

- Degree
- Betweenness
- Closeness
- Eigenvector
- PageRank

Allow users to compare rankings.

---

## Page 4 — Community Analysis

Show:

- Community graph
- Community sizes
- Modularity
- Community members
- Inter-community relationships

---

## Page 5 — Dependency Analysis

Identify:

- High-betweenness nodes
- High concentration relationships
- Bridge organizations
- Single-source dependencies
- Highly dependent downstream nodes

Be precise about what is directly supported by the network structure.

---

## Page 6 — Temporal Analysis

Show:

- Network evolution
- Centrality evolution
- Community evolution
- Node/edge growth
- Density over time

---

## Page 7 — Resilience Simulation

Allow the user to select:

```text
Random Failure
Degree Attack
Betweenness Attack
PageRank Attack
```

Then display:

- Nodes removed
- Components
- Largest component
- Efficiency
- Fragmentation
- Network degradation plot

---

# 27. Visualization Requirements

Visualization is a major part of the project.

Required visualizations:

### 1. Full network graph

### 2. Centrality heatmap

### 3. Degree distribution

### 4. Community-colored graph

### 5. Community size distribution

### 6. Centrality comparison

### 7. Temporal network metrics

### 8. Resilience curves

### 9. Dependency/bridge visualization

### 10. Geographic visualization if location data is included

Every visualization should answer a question.

Avoid decorative graphs.

---

# 28. Decentralized Data Layer

The decentralized component should remain lightweight.

Possible implementation:

- Hyperledger Fabric
- Ethereum-compatible private network
- Other permissioned ledger

For an academic prototype, a permissioned/private blockchain is preferable to building a public cryptocurrency system.

The ledger should demonstrate:

```text
Transaction created
        ↓
Transaction validated
        ↓
Transaction recorded
        ↓
Transaction retrieved
        ↓
Graph constructed
```

The SNA system consumes verified transaction records.

---

# 29. Important Separation of Concerns

Architecture:

```text
                DATA GENERATOR
                      │
                      ▼
             Synthetic Transactions
                      │
                      ▼
            Decentralized Ledger
                      │
                      ▼
             Transaction Extractor
                      │
                      ▼
               Graph Builder
                      │
                      ▼
            ┌──────────────────┐
            │   SNA ENGINE     │
            ├──────────────────┤
            │ Centrality       │
            │ Communities      │
            │ k-Core           │
            │ Temporal SNA     │
            │ Resilience       │
            └────────┬─────────┘
                     │
                     ▼
               Analytics API
                     │
                     ▼
              Visualization
                     │
                     ▼
             Research Findings
```

---

# 30. Recommended Technology Stack

## Data generation

Python

- NumPy
- Pandas
- Faker
- NetworkX

## SNA

Primary:

- NetworkX

Optionally benchmark with:

- igraph

## Visualization

- Plotly
- Streamlit

Optional:

- Cytoscape.js
- D3.js

## Blockchain

Prefer a lightweight permissioned implementation.

Possible:

- Hyperledger Fabric

Alternative:

- Ethereum-compatible private chain

The blockchain should not dominate development time.

## Storage

- PostgreSQL

Optional graph database:

- Neo4j

Neo4j is optional and should only be introduced if it materially improves graph querying/analysis.

---

# 31. Project Folder Structure

Recommended:

```text
supply-chain-sna/
│
├── README.md
├── requirements.txt
├── docker-compose.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   └── scenarios/
│
├── generator/
│   ├── organization_generator.py
│   ├── transaction_generator.py
│   ├── network_generator.py
│   ├── scenarios.py
│   └── config.yaml
│
├── blockchain/
│   ├── contracts/
│   ├── network/
│   └── transaction_service/
│
├── graph/
│   ├── builder.py
│   ├── preprocessing.py
│   └── graph_models.py
│
├── sna/
│   ├── centrality.py
│   ├── communities.py
│   ├── kcore.py
│   ├── network_metrics.py
│   ├── temporal.py
│   └── resilience.py
│
├── experiments/
│   ├── centrality_experiments.py
│   ├── community_experiments.py
│   ├── resilience_experiments.py
│   └── temporal_experiments.py
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   └── components/
│
├── tests/
│
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   └── experiments.ipynb
│
├── reports/
│   ├── figures/
│   └── results/
│
└── docs/
    ├── methodology.md
    ├── dataset.md
    └── architecture.md
```

---

# 32. Evaluation

The project must evaluate more than whether the dashboard works.

## Synthetic ground-truth evaluation

Because the data is synthetic, intentionally plant known structures.

Evaluate whether algorithms recover them.

Examples:

### Planted bridge

```text
Known bridge node = B
```

Check whether B appears among high-betweenness nodes.

### Planted communities

Generate:

```text
Community A
Community B
Community C
```

Check community-detection recovery.

Possible measures:

- Adjusted Rand Index
- Normalized Mutual Information
- Community modularity

### Known critical node

Remove it and verify whether the network degradation is detected.

---

# 33. Experiments

Minimum experiments:

## Experiment 1 — Centrality Comparison

Compare:

- Degree
- Betweenness
- Eigenvector
- PageRank

Determine where rankings agree and where they differ.

---

## Experiment 2 — Community Detection

Run community detection.

Evaluate:

- Number of communities
- Modularity
- Recovery of planted communities

---

## Experiment 3 — Network Resilience

Compare:

```text
Random removal
vs
Degree-based removal
vs
Betweenness-based removal
vs
PageRank-based removal
```

Do not decide the outcome in advance. Report what the experiments show.

---

## Experiment 4 — Temporal Evolution

Compare network structure across time.

---

## Experiment 5 — Hidden Dependency

Create known upstream dependencies and test whether network analysis exposes them.

---

# 34. Expected Research Outputs

The project should produce evidence-based findings such as:

- Which nodes have the highest degree?
- Which nodes have the highest betweenness?
- Which nodes are connected to influential organizations?
- How many communities exist?
- How stable are communities over time?
- Which organizations act as bridges?
- How fragmented does the network become after targeted failures?
- How does the network evolve?
- Which structural patterns indicate dependency concentration?

Do not manufacture conclusions.

All conclusions must be generated from the actual experimental results.

---

# 35. Research Report Structure

## 1. Introduction & Context

Include:

- Supply-chain background
- Network perspective
- Problem statement
- Relevance of SNA
- Research questions
- Objectives

The rubric expects a clear research problem, background, and explanation of why SNA is relevant.

---

## 2. Network Data Collection & Sources

Include:

- Synthetic dataset justification
- Dataset-generation methodology
- Data schema
- Synthetic assumptions
- Ground-truth construction
- Data limitations

Clearly state:

> The dataset is synthetic and is designed to reproduce realistic structural properties of supply-chain networks for controlled SNA experimentation.

---

## 3. Network Modeling & Methodology

Include:

- Node definition
- Edge definition
- Directed graph justification
- Weighted graph justification
- Centrality methods
- Community detection
- k-core
- Temporal SNA
- Resilience methodology

Each method must have a reason for being used.

---

## 4. Analysis & Interpretation

Present actual results.

Discuss:

- Centrality
- Communities
- Dependencies
- Temporal changes
- Resilience
- Network structure

Interpret the results in supply-chain terms.

---

## 5. Visualization & Graph Representation

Include high-quality:

- Network graphs
- Centrality charts
- Community visualizations
- Temporal visualizations
- Resilience plots

---

## 6. Discussion & Implications

Discuss:

- What the network reveals
- Supply-chain risk implications
- Dependency implications
- Potential decision-support use
- Limitations
- Future research

---

## 7. Conclusion

Summarize:

- Research questions
- Major findings
- SNA contribution
- Practical implications
- Future work

---

# 36. Limitations

Explicitly acknowledge:

- Synthetic data is not equivalent to real enterprise data
- Synthetic generation rules influence network structure
- SNA identifies structural patterns but does not automatically establish causation
- Centrality does not necessarily mean business importance
- Community detection depends on algorithm and network representation
- Missing/incorrect relationships can alter results
- Blockchain immutability does not guarantee that the original transaction was truthful

These limitations make the research more academically credible.

---

# 37. Future Work

Potential extensions:

- Real enterprise supply-chain datasets
- IoT-based supply-chain data
- ERP integration
- SAP/ERP transaction integration
- Graph neural networks
- Anomaly detection
- Supply-chain disruption prediction
- Real-time SNA
- Knowledge graphs
- Multi-layer networks
- Geographic risk modeling
- Carbon/emissions network analysis

---

# 38. What Claude Should Build

Claude should build the project incrementally.

## Phase 1 — Project foundation

Build:

- Repository
- Environment
- Configuration
- Logging
- Testing structure

---

## Phase 2 — Synthetic data generator

Build configurable generator producing:

- Organizations
- Transactions
- Communities
- Dependencies
- Hubs
- Bridges
- Temporal changes
- Failure scenarios

Generate reproducible datasets using a random seed.

---

## Phase 3 — Graph construction

Implement:

- Directed graph
- Weighted graph
- Time snapshots
- Graph validation

---

## Phase 4 — SNA engine

Implement:

- Degree
- Betweenness
- Closeness
- Eigenvector
- PageRank
- k-core
- Community detection
- Network-level metrics

---

## Phase 5 — Experiments

Implement:

- Centrality comparison
- Community evaluation
- Resilience experiments
- Temporal analysis
- Hidden dependency experiments

---

## Phase 6 — Visualization

Build the dashboard.

---

## Phase 7 — Decentralized layer

Integrate transaction recording/retrieval.

Keep this modular so SNA works even if the blockchain layer is temporarily disabled.

---

## Phase 8 — Evaluation and report artifacts

Automatically generate:

- CSV results
- JSON results
- PNG/SVG figures
- experiment summaries
- tables
- reproducibility metadata

---

# 39. Definition of Done

The project is complete when:

- [ ] Synthetic dataset generator works
- [ ] Dataset generation is reproducible
- [ ] Synthetic structural ground truth exists
- [ ] Transaction data is converted to a graph
- [ ] Directed/weighted network is supported
- [ ] Degree centrality implemented
- [ ] Betweenness centrality implemented
- [ ] Closeness centrality implemented
- [ ] Eigenvector centrality implemented
- [ ] PageRank implemented
- [ ] Community detection implemented
- [ ] k-core implemented
- [ ] Network-level metrics implemented
- [ ] Temporal SNA implemented
- [ ] Resilience experiments implemented
- [ ] Ground-truth evaluation implemented
- [ ] Interactive dashboard implemented
- [ ] Network visualizations implemented
- [ ] Results are exportable
- [ ] Blockchain/decentralized layer integrated or demonstrated
- [ ] Documentation exists
- [ ] Tests exist
- [ ] Research findings are generated from actual results
- [ ] Limitations are documented

---

# 40. Most Important Design Principle

**Do not build a blockchain project with an SNA component.**

Build:

> **An SNA research system for understanding supply-chain network structure, with decentralized transaction infrastructure as a supporting component.**

The research pipeline should be:

```text
Synthetic Supply Chain
        ↓
Transactions
        ↓
Trusted / Decentralized Data Layer
        ↓
Network Construction
        ↓
Social Network Analysis
        ↓
Centrality + Communities + Dependencies
        ↓
Temporal Analysis
        ↓
Resilience Experiments
        ↓
Visualization
        ↓
Evidence-Based Findings
```

The key output is not:

> "Here is a blockchain transaction."

The key output is:

> **"Here is what the structure of the supply-chain network tells us about influence, dependency, communities, and vulnerability."**

---

# 41. Rubric Alignment

The implementation and report should explicitly map to the case-study rubric.

| Rubric criterion | Project deliverable |
|---|---|
| Introduction & Context | Problem statement, research questions, SNA motivation |
| Network Data Collection & Sources | Synthetic-data methodology, schema, generation rules, limitations |
| Network Modeling & Methodology | Directed/weighted graph + justified SNA techniques |
| Analysis & Interpretation | Centrality, communities, dependency, temporal and resilience analysis |
| Visualization & Graph Representation | Interactive network graphs and analytical visualizations |
| Discussion & Implications | Supply-chain interpretation, applications, limitations, future work |
| Conclusion & Summary | Findings and SNA contribution |
| Overall Clarity & Presentation | Structured report, documentation, reproducible experiments |

The rubric emphasizes strong research context, justified SNA methodology, in-depth interpretation, effective visualizations, real-world implications, and clear conclusions. The implementation should therefore be designed around these outputs rather than around the blockchain technology itself.

---

# 42. Final Project Statement

> **This project develops a Social Network Analysis framework for studying decentralized supply-chain networks. Supply-chain organizations are represented as nodes and their transactions or business relationships as directed, weighted edges. Using centrality analysis, community detection, k-core analysis, temporal network analysis, and resilience simulations, the system identifies structurally important organizations, intermediary dependencies, network communities, hidden structural dependencies, and vulnerabilities. A decentralized transaction layer provides a trusted foundation for the transaction data used to construct the network. A synthetic but structurally realistic dataset enables controlled experiments and ground-truth evaluation. The final system provides an interactive analytics dashboard and evidence-based insights into supply-chain network structure and resilience.**

