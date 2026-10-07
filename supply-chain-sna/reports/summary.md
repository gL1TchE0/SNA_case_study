# Supply Chain Social Network Analysis — Research Summary

**Generated**: 2026-10-07 17:26 UTC  
**Seed**: 42  
**Dataset Version**: v1  

---

## 1. Dataset Statistics

- **Nodes**: 1000
- **Edges**: 5000
- **Density**: 0.005005
- **Weakly Connected Components**: 7
- **Largest WCC Fraction**: 0.9940
- **Average Total Degree**: 10.00
- **Avg Clustering (undirected)**: 0.0492
- **Global Efficiency**: 0.3182854521189821

---

## 2. Centrality Findings

### Top 3 by Total Degree
- WHS-00014: 75.000000
- MFG-00131: 70.000000
- WHS-00063: 65.000000
### Top 3 by Betweenness
- WHS-00014: 0.059729
- DST-00112: 0.055030
- WHS-00063: 0.050684
### Top 3 by Pagerank
- WHS-00041: 0.006118
- WHS-00014: 0.005071
- RET-00033: 0.004633
### Top 3 by Pagerank Reversed
- MFG-00028: 0.006896
- MFG-00131: 0.006227
- MFG-00141: 0.005303

### Rank Correlations (Spearman)
- total_degree_vs_betweenness: r = 0.6893
- total_degree_vs_pagerank: r = 0.7618
- betweenness_vs_pagerank: r = 0.6015
- eigenvector_vs_pagerank: r = 0.9466
- betweenness_vs_closeness: r = 0.5348
- total_degree_vs_pagerank_reversed: r = 0.1854
- pagerank_vs_pagerank_reversed: r = -0.2986

---

## 3. Community Detection

- **Algorithm**: louvain
- **Communities Detected**: 11
- **Inter-community Edge Fraction**: 0.1315

---

## 4. Dependency Analysis

- Logistics-provider edges are excluded from supplier counts
- **Nodes with >80% upstream concentration**: 34
- **Mean supplier dependency ratio**: 0.2914

---

## 5. Ground-Truth Evaluation

- **Hub recovery in top-20 by total_degree**: 1.00
- **Hub recovery in top-20 by betweenness**: 1.00
- **Hub recovery in top-20 by pagerank**: 0.00
- **Hub recovery in top-20 by pagerank_reversed**: 0.50
- **Bridge recovery in top-30 betweenness**: 1.0
- **Median betweenness rank of planted bridges**: 2.0
- **Median degree rank of planted bridges**: 1.0
- **Planted dependents whose top supplier is the planted critical supplier**: 1.00
- **Planted dependents flagged as high-dependency (top 10% of manufacturers)**: 0.33
- **Critical suppliers in top 10% of suppliers by weighted out-degree**: 1/1
- **Critical suppliers in top 10% of suppliers by reversed PageRank**: 1/1

---

## 7. Limitations

- Dataset is synthetic and not equivalent to real enterprise supply-chain data
- Synthetic generation rules influence network structure and SNA findings
- SNA identifies structural patterns but does not establish causation
- Centrality does not automatically imply business importance
- Community detection results depend on algorithm choice and graph representation
- Large-graph metrics (path length, efficiency) may use sampling approximations
- Blockchain/decentralized layer is abstracted, not a live implementation