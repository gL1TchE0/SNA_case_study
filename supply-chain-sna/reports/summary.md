# Supply Chain Social Network Analysis — Research Summary

**Generated**: 2026-10-01 05:28 UTC  
**Seed**: 42  
**Dataset Version**: v1  

---

## 1. Dataset Statistics

- **Nodes**: 1000
- **Edges**: 6806
- **Density**: 0.006813
- **Weakly Connected Components**: 2
- **Largest WCC Fraction**: 0.9990
- **Average Total Degree**: 13.61
- **Avg Clustering (undirected)**: 0.0704
- **Global Efficiency**: 0.34422492492410844

---

## 2. Centrality Findings

### Top 3 by Total Degree
- WHS-00014: 87.000000
- MFG-00141: 73.000000
- MFG-00131: 72.000000
### Top 3 by Betweenness
- WHS-00014: 0.052268
- DST-00112: 0.046097
- WHS-00063: 0.035812
### Top 3 by Pagerank
- WHS-00041: 0.005443
- WHS-00014: 0.004980
- RET-00067: 0.004886
### Top 3 by Pagerank Reversed
- MFG-00028: 0.006389
- MFG-00131: 0.005753
- MFG-00141: 0.005289

### Rank Correlations (Spearman)
- total_degree_vs_betweenness: r = 0.7084
- total_degree_vs_pagerank: r = 0.7636
- betweenness_vs_pagerank: r = 0.6016
- eigenvector_vs_pagerank: r = 0.9591
- betweenness_vs_closeness: r = 0.5189
- total_degree_vs_pagerank_reversed: r = 0.2194
- pagerank_vs_pagerank_reversed: r = -0.2500

---

## 3. Community Detection

- **Algorithm**: louvain
- **Communities Detected**: 6
- **Modularity**: 0.6530717900778058
- **Inter-community Edge Fraction**: 0.1238

---

## 4. Dependency Analysis

- Logistics-provider edges are excluded from supplier counts
- **Nodes with >80% upstream concentration**: 27
- **Mean supplier dependency ratio**: 0.2542

---

## 5. Temporal Analysis

- **Months analyzed**: 24
- **Node count range**: 760–905
- **Edge count range**: 3068–5034
- **Density trend**: 0.005319 → 0.006153
- **Detected communities per month**: 5–8
- **Modularity range**: 0.6047–0.6772

---

## 6. Resilience Findings

- **Random removal at 10%**: LCC = 0.9989
- **Degree removal at 10%**: LCC = 0.9911
- **Betweenness removal at 10%**: LCC = 0.9922
- **Pagerank removal at 10%**: LCC = 0.9978

---

## 7. Ground-Truth Evaluation

- **Hub recovery in top-20 by total_degree**: 0.80
- **Hub recovery in top-20 by betweenness**: 0.40
- **Hub recovery in top-20 by pagerank**: 0.00
- **Hub recovery in top-20 by pagerank_reversed**: 0.60
- **Bridge recovery in top-30 betweenness**: 0.9
- **Median betweenness rank of planted bridges**: 6.0
- **Median degree rank of planted bridges**: 10.0
- **Community ARI**: 0.9690234424583879
- **Community NMI**: 0.9549513376336983
- **Planted dependents whose top supplier is the planted critical supplier**: 1.00
- **Planted dependents flagged as high-dependency (top 10% of manufacturers)**: 0.67
- **Critical suppliers in top 10% of suppliers by weighted out-degree**: 3/3
- **Critical suppliers in top 10% of suppliers by reversed PageRank**: 3/3
- **Efficiency change after removing planted hubs**: -0.009198990422985776

---

## 8. Limitations

- Dataset is synthetic and not equivalent to real enterprise supply-chain data
- Synthetic generation rules influence network structure and SNA findings
- SNA identifies structural patterns but does not establish causation
- Centrality does not automatically imply business importance
- Community detection results depend on algorithm choice and graph representation
- Large-graph metrics (path length, efficiency) may use sampling approximations
- Blockchain/decentralized layer is abstracted, not a live implementation