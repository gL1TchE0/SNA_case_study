# BUILD_DECISIONS.md
# Architectural and Methodological Decisions

## Graph Representation
- **Decision**: Use `networkx.DiGraph` as primary graph representation
- **Rationale**: Supply chains have directional flow (Supplier → Manufacturer → Distributor → Retailer). Direction is meaningful and must be preserved.
- **Weight semantics**: Multiple weight modes supported:
  - `frequency` = transaction count between node pairs
  - `quantity` = total quantity exchanged
  - `transaction_value` = total monetary value

## Temporal Snapshots
- **Decision**: Monthly snapshots built from that month's transactions only (`snapshots.mode: monthly`). Only organizations that transacted in the month are nodes.
- **Rationale**: A monthly window shows the network as it actually was in that month, so organization entries, exits and dropped relationships are visible. Leaving inactive organizations in as isolated nodes would inflate the component count and deflate density for reasons that have nothing to do with structure.
- **Alternative available**: `snapshots.mode: cumulative` builds each snapshot from all transactions up to and including that month. It can only grow, so it hides exits; it is kept as an option, not the default.

## Community Detection Algorithm
- **Decision**: Louvain as primary (on undirected projection of DiGraph)
- **Rationale**: Louvain is widely used, fast, and produces good modularity. Greedy modularity provided as secondary option.
- **Note**: Community detection applied on undirected version of graph since Louvain requires undirected input. Documented in methodology.

## Closeness Centrality on Disconnected Graphs
- **Decision**: Use NetworkX `closeness_centrality` with default Wasserman-Faust normalization
- **Rationale**: This handles disconnected graphs by computing within connected components. Explicitly documented.

## Eigenvector Centrality Convergence
- **Decision**: Use `max_iter=1000`, `tol=1e-6`, fallback to PageRank if convergence fails
- **Rationale**: Directed graphs may have convergence issues. PageRank is a valid alternative for measuring importance in directed networks.

## Resilience Random Removal
- **Decision**: Run 10 seeds, report mean ± std
- **Rationale**: Single random run is statistically misleading. Multiple seeds provide reliable estimate.

## Synthetic Data Realism
- **Decision**: Use hierarchical generation with power-law degree heterogeneity
- **Rationale**: Real supply chains have hub organizations with many connections and peripheral organizations with few. Uniform random generation would not produce this.

## Decentralized Layer
- **Decision**: Implement `SyntheticTransactionStore` + abstract `TransactionStore` interface. No real blockchain required.
- **Rationale**: Real blockchain (Hyperledger/Ethereum) would significantly increase build complexity without improving SNA research objective. The abstraction allows future integration.

## Betweenness Centrality
- **Decision**: Use normalized, unweighted betweenness on directed graph
- **Rationale**: Normalization allows comparison across different network sizes. Directed betweenness correctly identifies intermediaries in directional flow. Edge weight is transaction frequency, which is a strength rather than a distance, so it is not used as a path cost.

## Edge Weights in Centrality
- **Decision**: PageRank and eigenvector centrality use edge weights (transaction frequency). Degree, betweenness and closeness are unweighted.
- **Rationale**: PageRank and eigenvector distribute importance in proportion to tie strength, where a weight is meaningful. Shortest-path measures would need a cost, and frequency is not one.

## Reversed PageRank
- **Decision**: Report PageRank on both the original and the edge-reversed graph.
- **Rationale**: Edges point downstream (supplier → buyer), so standard PageRank accumulates at sinks and ranks retailers highest. PageRank on the reversed graph accumulates at sources of supply and measures upstream importance, which is the relevant notion for supply risk.

## Dependency Analysis
- **Decision**: Logistics-provider edges are excluded when counting an organization's suppliers and computing its supplier dependency ratio.
- **Rationale**: A logistics provider moves goods but does not supply material. Counting it made many suppliers look single-sourced on their carrier.

## Planted Structures
- **Communities**: regions. Non-planted edges stay inside their region with probability `intra_community_edge_prob` (0.92), including relationships formed later.
- **Bridges**: distributors and warehouses that collect goods in their own region and ship to several organizations in other regions. Logistics providers are not used because they have no inbound edges in this model and so can never lie on a shortest path.
- **Dependency groups**: one critical supplier feeds several manufacturers at `dependency_volume_multiplier` times normal volume, so those manufacturers depend on it for most of their inbound volume.
- **Planted organizations are protected** from late entry and exit so the ground truth exists in every snapshot.

## Reproducibility
- **Decision**: Every random draw is taken from a sorted list.
- **Rationale**: The generator previously sampled from Python sets, whose iteration order changes between interpreter runs, so the same seed could give different datasets.

## K-Core Analysis
- **Decision**: Run k-core on undirected projection
- **Rationale**: NetworkX k-core decomposition requires undirected graphs. The undirected projection preserves connectivity information needed for core analysis.
