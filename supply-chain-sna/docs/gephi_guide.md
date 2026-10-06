# Using Gephi with this project

Gephi is used as a second, independent tool: to draw the network and to recompute the main statistics so they can be checked against the NetworkX results.

## 1. Export the graph

```bash
python -m graph.export_gephi
```

This writes `data/exports/supply_chain.gexf`. Every node carries its organization attributes, the NetworkX results (columns prefixed `nx_`), and `planted_role` (hub, bridge, critical_supplier, dependent_manufacturer or none).

## 2. Open and lay out

1. Gephi → File → Open → `supply_chain.gexf`. Keep graph type **Directed**.
2. Layout → **ForceAtlas 2**. Tick *Prevent Overlap* and *LinLog mode*, run until it settles, then stop.
3. Appearance → Nodes → Colour → Partition → `region` (or `organization_type`, `nx_community`, `planted_role`).
4. Appearance → Nodes → Size → Ranking → `nx_betweenness` or `nx_total_degree`.

## 3. Compute the statistics in Gephi

Run these from the Statistics panel. The settings matter for a fair comparison.

| Gephi statistic | Setting to use | Column it creates |
|---|---|---|
| Average Degree | — | `indegree`, `outdegree`, `degree` |
| Network Diameter | Directed, tick *Normalize centralities in [0,1]* | `betweenesscentrality`, `closnesscentrality` |
| PageRank | Directed, probability 0.85, epsilon 0.000001, tick *Use edge weight* | `pageranks` |
| Eigenvector Centrality | Directed, 1000 iterations | `eigencentrality` |
| Modularity | Resolution 1.0, untick *Use weights* is optional | `modularity_class` |

## 4. Export and compare

1. Data Laboratory → Export table → nodes, all columns → save as `data/exports/gephi_statistics.csv`.
2. Run:

```bash
python -m graph.compare_gephi data/exports/gephi_statistics.csv
```

It prints, for each metric, the Spearman rank correlation with the NetworkX value, how many of the top 20 organizations coincide, and the largest absolute difference, and saves the table to `reports/tables/gephi_comparison.csv`.

## What to expect

- **Degree**: identical.
- **PageRank**: near-identical when *Use edge weight* is ticked.
- **Betweenness**: identical ranking; values match only if normalization is ticked.
- **Eigenvector**: same ranking, different scale. Gephi scales the largest value to 1; NetworkX scales the vector to unit length.
- **Closeness**: expect the largest disagreement. Gephi averages over reachable nodes only; NetworkX applies the Wasserman–Faust correction and measures inbound distance.
- **Modularity**: Louvain is randomized, so community labels differ between runs. Compare the number of communities and the agreement score the script prints, not the labels.
