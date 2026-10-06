"""
Supply Chain SNA — Temporal SNA
PHASE 13: Tracks network metrics and centrality across time snapshots.

Produces time-series data showing how the network structure evolves:
  - Node/edge counts
  - Density
  - Components
  - Centrality changes per node
  - Community evolution
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)


def analyze_temporal_snapshots(
    temporal_graphs: dict[str, nx.DiGraph],
    top_n_nodes: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Compute SNA metrics across all temporal graph snapshots.

    Args:
        temporal_graphs: Dict mapping month ("YYYY-MM") → DiGraph.
        top_n_nodes: Number of top nodes to track centrality for.

    Returns:
        Tuple of:
            - snapshot_metrics: DataFrame with per-month network statistics
            - node_centrality_time: DataFrame with per-node centrality over time
            - summary: Dictionary with overall temporal findings
    """
    from sna.network_metrics import compute_network_statistics
    from sna.degree import compute_degree
    from sna.betweenness import compute_betweenness
    from sna.pagerank import compute_pagerank
    from sna.communities import compute_communities

    snapshot_records: list[dict[str, Any]] = []
    node_centrality_records: list[dict[str, Any]] = []

    months = sorted(temporal_graphs.keys())
    logger.info("Analyzing %d temporal snapshots…", len(months))

    for month in months:
        G = temporal_graphs[month]
        if G.number_of_nodes() == 0:
            continue

        # Network-level stats
        stats = compute_network_statistics(G)
        _, comm_stats = compute_communities(G)
        snapshot_records.append(
            {
                "month": month,
                "num_nodes": stats["num_nodes"],
                "num_edges": stats["num_edges"],
                "density": stats["density"],
                "weakly_connected_components": stats["weakly_connected_components"],
                "largest_wcc_fraction": stats["largest_wcc_fraction"],
                "avg_total_degree": stats["avg_total_degree"],
                "global_efficiency": stats.get("global_efficiency"),
                "avg_clustering": stats.get("avg_clustering_undirected"),
                "num_communities": comm_stats.get("num_communities"),
                "modularity": comm_stats.get("modularity"),
            }
        )

        # Per-node centrality for top nodes
        degree_df = compute_degree(G)
        top_nodes = degree_df.head(top_n_nodes)["node"].tolist()

        betweenness_df = compute_betweenness(G)
        pagerank_df = compute_pagerank(G)

        bet_map = dict(zip(betweenness_df["node"], betweenness_df["betweenness"]))
        pr_map = dict(zip(pagerank_df["node"], pagerank_df["pagerank"]))
        deg_map = dict(zip(degree_df["node"], degree_df["total_degree"]))

        for node in top_nodes:
            node_centrality_records.append(
                {
                    "month": month,
                    "node": node,
                    "total_degree": int(deg_map.get(node, 0)),
                    "betweenness": float(bet_map.get(node, 0.0)),
                    "pagerank": float(pr_map.get(node, 0.0)),
                }
            )

    snapshot_df = pd.DataFrame(snapshot_records)
    node_centrality_df = pd.DataFrame(node_centrality_records)

    # ── Summary statistics ────────────────────────────────────────────────────
    summary: dict[str, Any] = {}

    if not snapshot_df.empty:
        summary["months_analyzed"] = len(snapshot_df)
        summary["node_count_range"] = {
            "min": int(snapshot_df["num_nodes"].min()),
            "max": int(snapshot_df["num_nodes"].max()),
        }
        summary["edge_count_range"] = {
            "min": int(snapshot_df["num_edges"].min()),
            "max": int(snapshot_df["num_edges"].max()),
        }
        summary["density_trend"] = {
            "start": float(snapshot_df.iloc[0]["density"]),
            "end": float(snapshot_df.iloc[-1]["density"]),
            "direction": "increasing" if snapshot_df.iloc[-1]["density"] > snapshot_df.iloc[0]["density"] else "decreasing",
        }

    logger.info(
        "Temporal analysis: %d snapshots, %d node-month records",
        len(snapshot_df),
        len(node_centrality_df),
    )
    return snapshot_df, node_centrality_df, summary
