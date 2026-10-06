"""
Supply Chain SNA — Hidden Dependency Analysis
PHASE 12: Structural detection of supply-chain dependencies.

Defines explicit, measurable dependency metrics rather than vague
\"risk\" labels. All metrics are derived from network structure and
transaction volumes.

Metrics implemented:
  1. Supplier concentration ratio: fraction of a node's supply from one supplier
  2. Common upstream ancestor: nodes sharing the same critical upstream node
  3. High-betweenness dependency: dependency concentrated through bridge nodes
  4. Single-source detection: nodes with only one upstream supplier
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)

NON_SUPPLIER_TYPE = "logistics_provider"


def analyze_dependencies(
    G: nx.DiGraph,
    centrality_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Analyze structural dependencies in the supply-chain network.

    Args:
        G: Directed supply-chain graph with edge weights.
        centrality_df: Optional pre-computed centrality DataFrame with
            columns: node, betweenness. Used to identify bridge-based
            dependencies.

    Returns:
        Dictionary containing:
            single_source_nodes: nodes with only 1 upstream supplier
            upstream_concentration: DataFrame of dependency concentration
            high_betweenness_bridges: bridges with high dependency
            dependency_groups: groups sharing critical upstream nodes
    """
    results: dict[str, Any] = {}

    # Logistics providers move goods but do not supply material, so their
    # edges are not counted as supply dependencies.
    def _suppliers(node: str) -> list[str]:
        return [
            p for p in G.predecessors(node)
            if G.nodes[p].get("organization_type", "") != NON_SUPPLIER_TYPE
        ]

    # ── 1. Single-source dependency ───────────────────────────────────────────
    # Nodes whose entire upstream supply comes from one predecessor
    single_source: list[dict[str, Any]] = []
    for node in G.nodes():
        predecessors = _suppliers(node)
        if len(predecessors) == 1:
            pred = predecessors[0]
            single_source.append(
                {
                    "node": node,
                    "node_type": G.nodes[node].get("organization_type", ""),
                    "sole_supplier": pred,
                    "supplier_type": G.nodes[pred].get("organization_type", ""),
                }
            )

    results["single_source_nodes"] = single_source
    results["single_source_count"] = len(single_source)
    results["dependency_note"] = (
        "Supplier counts and concentration ratios exclude logistics-provider edges"
    )

    # ── 2. Upstream concentration ratio ──────────────────────────────────────
    # For each node, what fraction of its total incoming weight comes from
    # its top supplier?
    #   supplier_dependency_ratio = weight_from_top_supplier / total_weight
    concentration_records: list[dict[str, Any]] = []
    for node in G.nodes():
        predecessors = _suppliers(node)
        if not predecessors:
            continue

        incoming_weights = {
            pred: G[pred][node].get("weight", 1.0) for pred in predecessors
        }
        total_weight = sum(incoming_weights.values())
        if total_weight == 0:
            continue

        top_supplier = max(incoming_weights, key=incoming_weights.get)
        top_weight = incoming_weights[top_supplier]
        concentration_ratio = top_weight / total_weight

        concentration_records.append(
            {
                "node": node,
                "node_type": G.nodes[node].get("organization_type", ""),
                "num_suppliers": len(predecessors),
                "top_supplier": top_supplier,
                "top_supplier_type": G.nodes[top_supplier].get("organization_type", ""),
                "supplier_dependency_ratio": round(concentration_ratio, 4),
                "total_upstream_weight": round(total_weight, 2),
            }
        )

    concentration_df = pd.DataFrame(concentration_records)
    if not concentration_df.empty:
        concentration_df = concentration_df.sort_values(
            "supplier_dependency_ratio", ascending=False
        ).reset_index(drop=True)

    results["upstream_concentration"] = concentration_df
    results["high_concentration_count"] = (
        int((concentration_df["supplier_dependency_ratio"] > 0.8).sum())
        if not concentration_df.empty
        else 0
    )

    # ── 3. Common upstream ancestor detection ─────────────────────────────────
    # Find manufacturers/distributors that many downstream nodes depend on
    downstream_counts: dict[str, int] = {}
    for node in G.nodes():
        downstream = list(G.successors(node))
        downstream_counts[node] = len(downstream)

    # Nodes with many downstream dependencies (top quartile)
    if downstream_counts:
        counts_series = pd.Series(downstream_counts)
        threshold = counts_series.quantile(0.90)
        critical_upstream = counts_series[counts_series >= threshold].to_dict()
    else:
        critical_upstream = {}

    results["critical_upstream_nodes"] = [
        {
            "node": node,
            "node_type": G.nodes[node].get("organization_type", ""),
            "downstream_count": count,
        }
        for node, count in sorted(critical_upstream.items(), key=lambda x: -x[1])
    ]

    # ── 4. Bridge-based dependency ────────────────────────────────────────────
    if centrality_df is not None and "betweenness" in centrality_df.columns:
        top_n = min(20, len(centrality_df))
        bridge_nodes = centrality_df.nlargest(top_n, "betweenness")["node"].tolist()
        bridge_dependency = []
        for bridge in bridge_nodes:
            downstream = list(G.successors(bridge))
            upstream = list(G.predecessors(bridge))
            bridge_dependency.append(
                {
                    "bridge_node": bridge,
                    "bridge_type": G.nodes[bridge].get("organization_type", ""),
                    "betweenness": float(
                        centrality_df[centrality_df["node"] == bridge]["betweenness"].values[0]
                    ) if len(centrality_df[centrality_df["node"] == bridge]) > 0 else 0.0,
                    "upstream_count": len(upstream),
                    "downstream_count": len(downstream),
                }
            )
        results["high_betweenness_bridges"] = bridge_dependency
    else:
        results["high_betweenness_bridges"] = []

    logger.info(
        "Dependency analysis: %d single-source nodes, %d high-concentration, %d critical upstream",
        results["single_source_count"],
        results["high_concentration_count"],
        len(results["critical_upstream_nodes"]),
    )
    return results
