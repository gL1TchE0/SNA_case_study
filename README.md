# 🔗 Supply Chain Social Network Analysis (SNA)

A comprehensive Social Network Analysis platform for modeling, analyzing, and visualizing supply-chain networks. Built with a synthetic data generator, graph analytics engine, interactive dashboard, and a pluggable decentralized transaction layer.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
  - [Option A: Full Pipeline (Bash)](#option-a-full-pipeline-bash)
  - [Option B: Step-by-Step (Python)](#option-b-step-by-step-python)
  - [Quick Smoke Test](#quick-smoke-test)
- [Interactive Dashboard](#interactive-dashboard)
- [Running Individual Experiments](#running-individual-experiments)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Output & Reports](#output--reports)
- [Methodology & Design Decisions](#methodology--design-decisions)
- [Limitations](#limitations)
- [Tech Stack](#tech-stack)

---

## Overview

This project applies **Social Network Analysis** techniques to a supply-chain context. It generates a realistic synthetic supply-chain network (organizations, transactions, temporal dynamics) and then runs a full suite of graph-theoretic analyses to uncover structural patterns like:

- **Hub organizations** with outsized connectivity
- **Bridge nodes** that link disparate parts of the network
- **Community clusters** reflecting regional or industry groupings
- **Critical dependencies** and single-source supply risks
- **Network resilience** under random vs. targeted disruptions
- **Temporal evolution** of the network over 24 months

The entire pipeline — from data generation to report output — is reproducible and configurable via YAML.

---

## Key Features

| Feature | Description |
|---|---|
| **Synthetic Data Generator** | Produces organizations (with type, region, industry, size), edges with power-law degree distribution, transactions with pricing/quantity, and temporal dynamics (entry/exit, disruptions, seasonality) |
| **Graph Construction** | Builds a `networkx.DiGraph` with configurable edge weights (`frequency`, `quantity`, `transaction_value`) |
| **Centrality Analysis** | Degree (in/out/total), Betweenness, Closeness, Eigenvector, and PageRank — with rank correlation (Spearman) |
| **Community Detection** | Louvain algorithm on undirected projection; modularity score and inter-community edge analysis |
| **K-Core Decomposition** | Identifies the densely connected core of the network |
| **Hidden Dependency Analysis** | Computes supplier dependency ratios, single-source nodes, and critical upstream organizations |
| **Temporal SNA** | Monthly cumulative snapshots tracking node/edge count, density, centrality evolution over time |
| **Resilience Testing** | Node-removal experiments comparing Random, Degree, Betweenness, and PageRank attack strategies (multi-seed) |
| **Ground-Truth Evaluation** | Validates SNA findings against planted structural features (hubs, bridges, communities, dependency groups) |
| **Interactive Dashboard** | 7-page Streamlit app with Plotly visualizations for exploring all analytics |
| **Report Generation** | Automated Markdown summary, CSV tables, and Plotly figures |
| **Decentralized Backend** | Abstract `TransactionStore` interface with `SyntheticTransactionStore` (CSV-backed) and a `BlockchainTransactionStore` placeholder for future Hyperledger/Ethereum integration |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Configuration (YAML)                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 1–5: Data Generation (generator/)               │
│  Organization Generator → Network Generator → Transaction Generator│
│                    → Temporal Dynamics → Validation                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  CSV + JSON (ground_truth)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PHASE 6: Graph Builder (graph/)                   │
│             CSV → networkx.DiGraph (frequency/quantity)            │
│                  + Monthly Temporal Snapshots                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  Pickle (.pkl)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 7–16: SNA Engine (sna/ + experiments/)          │
│  Network Stats │ Centrality │ Communities │ K-Core │ Dependencies  │
│           Temporal │ Resilience │ Ground-Truth Validation          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  CSV + JSON
                                 ▼
┌──────────────────────────┬──────────────────────────────────────────┐
│  PHASE 17: Visualization │   PHASE 18: Streamlit Dashboard         │
│  (reports/visualization) │   (dashboard/app.py)                    │
│  Plotly Figures + Tables │   7-page interactive analytics          │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

## Project Structure

```
supply-chain-sna/
├── config/                          # Configuration files
│   ├── __init__.py                  # YAML config loader & merger
│   ├── default.yaml                 # Full default config (1000 orgs, 24 months)
│   └── smoke.yaml                   # Small config for quick pipeline validation
│
├── generator/                       # Synthetic data generation
│   ├── organization_generator.py    # Creates orgs with types, regions, industries
│   ├── network_generator.py         # Power-law edge generation with planted hubs/bridges
│   ├── transaction_generator.py     # Pricing, quantity, and transaction records
│   ├── temporal_generator.py        # Entry/exit, disruptions, seasonal dynamics
│   └── generate.py                  # CLI entry point: python -m generator.generate
│
├── graph/                           # Graph construction
│   ├── builder.py                   # Builds networkx.DiGraph + temporal snapshots
│   ├── validation.py                # Validates graph integrity
│   └── build.py                     # CLI entry point: python -m graph.build
│
├── sna/                             # SNA analysis modules
│   ├── network_metrics.py           # Global stats (density, WCC, clustering, efficiency)
│   ├── centrality.py                # Orchestrates all centrality computations
│   ├── degree.py                    # In/out/total degree centrality
│   ├── betweenness.py               # Normalized betweenness on directed graph
│   ├── closeness.py                 # Wasserman-Faust closeness (handles disconnected)
│   ├── eigenvector.py               # Eigenvector centrality with PageRank fallback
│   ├── pagerank.py                  # PageRank centrality
│   ├── communities.py               # Louvain community detection + modularity
│   ├── kcore.py                     # K-core decomposition (on undirected projection)
│   ├── dependencies.py              # Upstream concentration & single-source analysis
│   ├── temporal.py                  # Temporal snapshot analysis
│   └── resilience.py                # Random vs. targeted node-removal experiments
│
├── experiments/                     # Experiment orchestration
│   ├── run.py                       # CLI: python -m experiments.run --experiment all
│   └── ground_truth.py              # Ground-truth structural evaluation
│
├── reports/                         # Report generation & visualization
│   ├── generate.py                  # CLI: python -m reports.generate
│   ├── visualization.py             # Plotly figure generation
│   ├── summary.md                   # Auto-generated research summary
│   ├── figures/                     # Generated Plotly figure exports
│   ├── results/                     # Experiment output CSVs and JSONs
│   └── tables/                      # Formatted CSV tables for reporting
│
├── dashboard/                       # Interactive analytics dashboard
│   └── app.py                       # Streamlit 7-page dashboard
│
├── blockchain/                      # Decentralized transaction layer
│   └── transaction_service/
│       └── __init__.py              # TransactionStore interface + implementations
│
├── tests/                           # Unit tests
│   └── test_sna.py                  # pytest test suite
│
├── data/                            # Generated data (gitignored)
│   ├── synthetic/                   # organizations.csv, transactions.csv, ground_truth.json
│   └── processed/                   # Pickle graph files (.pkl)
│
├── requirements.txt                 # Python dependencies
├── run_pipeline.sh                  # Bash script to run the full pipeline
├── BUILD_DECISIONS.md               # Architectural & methodological rationale
└── BUILD_PROGRESS.md                # Phase-by-phase build checklist
```

---

## Prerequisites

- **Python 3.10+** (uses `X | Y` union type syntax and `match` statements)
- **pip** (or any Python package manager)
- **Git** (to clone the repository)
- **(Optional)** Bash shell — for `run_pipeline.sh`. Windows users can run steps individually via Python (see below).

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/unstoppableh3r0/SNA_case_study.git
cd SNA_case_study/supply-chain-sna
```

### 2. Create a Virtual Environment

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:

| Category | Packages |
|---|---|
| Core | `numpy`, `pandas`, `scipy` |
| Graph Analysis | `networkx`, `python-louvain` |
| Data Generation | `Faker` |
| Visualization | `plotly`, `matplotlib`, `kaleido` |
| Dashboard | `streamlit` |
| Configuration | `PyYAML` |
| Testing | `pytest`, `pytest-cov` |
| Utilities | `tqdm`, `python-dateutil` |

---

## Running the Project

### Option A: Full Pipeline (Bash)

> **Note:** This script uses `.venv/bin/python3` paths — Linux/macOS only. Windows users should use Option B.

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

Or with a custom config:
```bash
./run_pipeline.sh config/smoke.yaml
```

The script runs all four stages automatically:
1. **Data Generation** → `data/synthetic/`
2. **Graph Building** → `data/processed/`
3. **Experiments** → `reports/results/`
4. **Report Generation** → `reports/`

### Option B: Step-by-Step (Python)

Run each stage independently. This works on **all platforms** (Windows, Linux, macOS).

```bash
# Step 1: Generate synthetic supply-chain data
python -m generator.generate --config config/default.yaml

# Step 2: Build the NetworkX graph from generated data
python -m graph.build --config config/default.yaml

# Step 3: Run all SNA experiments
python -m experiments.run --config config/default.yaml --experiment all

# Step 4: Generate reports, figures, and tables
python -m reports.generate --config config/default.yaml
```

> **Important:** Always run from the project root directory (`supply-chain-sna/`).

### Quick Smoke Test

For rapid pipeline validation with a smaller dataset (100 orgs, 3 months):

```bash
python -m generator.generate --config config/smoke.yaml
python -m graph.build --config config/smoke.yaml
python -m experiments.run --config config/smoke.yaml --experiment all
python -m reports.generate --config config/smoke.yaml
```

---

## Interactive Dashboard

After running the pipeline, launch the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501` and provides **7 interactive pages**:

| Page | Description |
|---|---|
| 📊 **Overview** | KPI cards (nodes, edges, density, communities), organization type/region distributions, monthly transaction volume |
| 🌐 **Network Explorer** | Interactive graph visualization with filters (org type, color-by), node detail lookup |
| 📈 **Centrality Analysis** | Top-N organizations by Degree, Betweenness, PageRank, Closeness; rank correlation charts; degree distribution |
| 🏘️ **Community Analysis** | Community sizes, modularity, member lookup; ground-truth ARI/NMI evaluation |
| ⚠️ **Dependency Analysis** | Supplier dependency ratios, single-source nodes, critical upstream nodes, bridge organizations |
| ⏱️ **Temporal Analysis** | Network evolution over time, per-node centrality tracking across months |
| 🛡️ **Resilience Simulation** | Degradation curves comparing Random vs. Degree vs. Betweenness vs. PageRank attack strategies |

---

## Running Individual Experiments

You can run specific experiments instead of the full suite:

```bash
# Centrality metrics only (also runs K-Core and Dependencies)
python -m experiments.run --experiment centrality

# Community detection only
python -m experiments.run --experiment communities

# Resilience testing only
python -m experiments.run --experiment resilience

# Temporal analysis only
python -m experiments.run --experiment temporal

# Ground-truth evaluation only (requires centrality to have been run first)
python -m experiments.run --experiment ground_truth
```

---

## Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=sna --cov=generator --cov=graph --cov-report=term-missing
```

---

## Configuration

All parameters are controlled via YAML configuration files in `config/`.

### Key Configuration Sections

| Section | Parameters | Description |
|---|---|---|
| `network` | `organizations`, `months`, `start_date`, `target_edges` | Network size and time span |
| `organization_types` | Proportions for supplier, manufacturer, distributor, etc. | Controls the type distribution |
| `regions` | List of region names | Geographic regions for orgs |
| `industries` | List of industry names | Industry classifications |
| `planted_structures` | `num_hubs`, `num_bridges`, `num_communities`, `num_dependency_groups` | Ground-truth features injected into the network for validation |
| `temporal` | `organization_entry_rate`, `disruption_months`, `seasonal_peak_months` | Controls network evolution dynamics |
| `resilience` | `removal_fractions`, `random_seeds` | Resilience experiment parameters |
| `centrality` | `eigenvector_max_iter`, `pagerank_alpha` | Algorithm hyperparameters |
| `community` | `algorithm`, `louvain_resolution` | Community detection settings |
| `output` | `data_dir`, `graph_dir`, `reports_dir`, etc. | Output directory paths |

### Creating a Custom Configuration

Copy and modify `config/default.yaml`:

```bash
cp config/default.yaml config/custom.yaml
# Edit config/custom.yaml with your parameters
python -m generator.generate --config config/custom.yaml
```

---

## Output & Reports

After a full pipeline run, the following outputs are generated:

```
data/
├── synthetic/
│   ├── organizations.csv          # Organization master data
│   ├── transactions.csv           # All transaction records
│   └── ground_truth.json          # Planted hubs, bridges, communities, dependency groups
└── processed/
    ├── supply_chain_graph_frequency.pkl     # Main graph (edge weight = transaction count)
    └── temporal_graphs_frequency.pkl        # Monthly snapshot graphs

reports/
├── summary.md                     # Auto-generated research summary
├── results/
│   ├── centrality.csv             # Per-node centrality scores
│   ├── centrality_stats.json      # Rank correlations and statistics
│   ├── communities.csv            # Community assignments
│   ├── community_stats.json       # Modularity and community stats
│   ├── kcore.csv                  # K-core decomposition
│   ├── dependencies.csv           # Upstream concentration per node
│   ├── dependency_summary.json    # Single-source and critical node counts
│   ├── network_statistics.json    # Global network metrics
│   ├── temporal.csv               # Temporal snapshot metrics
│   ├── temporal_centrality.csv    # Per-node centrality over time
│   ├── resilience_random.csv      # Resilience results (random removal)
│   ├── resilience_degree.csv      # Resilience results (degree-targeted)
│   ├── resilience_betweenness.csv # Resilience results (betweenness-targeted)
│   ├── resilience_pagerank.csv    # Resilience results (pagerank-targeted)
│   ├── ground_truth_results.json  # Hub, bridge, community, dependency recovery
│   └── summary.json              # Run metadata
├── figures/                       # Exported Plotly charts (PNG)
└── tables/                        # Formatted CSV tables for reporting
```

---

## Methodology & Design Decisions

Key architectural and methodological choices are documented in [`BUILD_DECISIONS.md`](BUILD_DECISIONS.md). Highlights:

- **Directed Graph**: Supply chains have directional flow (Supplier → Manufacturer → Distributor → Retailer), so `networkx.DiGraph` is used.
- **Louvain on Undirected Projection**: Community detection requires undirected graphs; the directed graph is projected before applying Louvain.
- **Eigenvector → PageRank Fallback**: If eigenvector centrality fails to converge on the directed graph, PageRank is used as a fallback.
- **Multi-Seed Resilience**: Random removal uses 10 seeds with mean ± std for statistical reliability.
- **Cumulative Temporal Snapshots**: Each monthly snapshot includes all transactions up to that month (not a sliding window).
- **Decoupled Transaction Layer**: The SNA engine only consumes DataFrames — it doesn't know or care whether data comes from CSV files or a blockchain.

---

## Limitations

- Dataset is synthetic and not equivalent to real enterprise supply-chain data
- Synthetic generation rules influence network structure and SNA findings
- SNA identifies structural patterns but does not establish causation
- Centrality does not automatically imply business importance
- Community detection results depend on algorithm choice and graph representation
- Large-graph metrics (path length, efficiency) may use sampling approximations
- Blockchain/decentralized layer is abstracted, not a live implementation

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Graph Engine | NetworkX |
| Community Detection | python-louvain |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Data Generation | Faker, NumPy, Pandas |
| Configuration | PyYAML |
| Testing | pytest |
| Image Export | Kaleido |

---

## License

This project is developed as an academic case study for Social Network Analysis coursework.

---

<p align="center">
  Built with ❤️ using Python, NetworkX, and Streamlit
</p>
