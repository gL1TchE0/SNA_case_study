# Supply Chain Social Network Analysis — Research Summary

**Generated**: 2026-10-08 03:57 UTC  
**Seed**: 42  
**Dataset Version**: v1  

---

## 1. Dataset Statistics

- **Nodes**: 994
- **Edges**: 5000
- **Density**: 0.005066
- **Weakly Connected Components**: 1
- **Largest WCC Fraction**: 1.0000
- **Average Total Degree**: 10.06
- **Avg Clustering (undirected)**: 0.0495
- **Global Efficiency**: 0.3221414759117273

---

## 2. Centrality Findings

### Top 3 by Total Degree
- WHS-00014: 75.000000
- MFG-00131: 70.000000
- WHS-00063: 65.000000
### Top 3 by Betweenness
- WHS-00014: 0.060453
- DST-00112: 0.055697
- WHS-00063: 0.051299
### Top 3 by Pagerank
- WHS-00041: 0.006132
- WHS-00014: 0.005083
- RET-00033: 0.004643
### Top 3 by Pagerank Reversed
- MFG-00028: 0.006917
- MFG-00131: 0.006245
- MFG-00141: 0.005319

### Rank Correlations (Spearman)
- total_degree_vs_betweenness: r = 0.6881
- total_degree_vs_pagerank: r = 0.7599
- betweenness_vs_pagerank: r = 0.5985
- eigenvector_vs_pagerank: r = 0.9457
- betweenness_vs_closeness: r = 0.5311
- total_degree_vs_pagerank_reversed: r = 0.1734
- pagerank_vs_pagerank_reversed: r = -0.3107

---

## 3. Community Detection

- **Algorithm**: louvain
- **Communities Detected**: 5
- **Inter-community Edge Fraction**: 0.1337

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