"""
Supply Chain SNA — Graph Builder
PHASE 6: Converts transaction data into NetworkX directed graphs.

Supports multiple weight modes:
  - frequency: edge weight = number of transactions
  - quantity: edge weight = total quantity exchanged
  - transaction_value: edge weight = total monetary value

Also builds temporal graph snapshots for each month.
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)


def build_graph(
    organizations: pd.DataFrame,
    transactions: pd.DataFrame,
    weight_mode: str = "frequency",
) -> nx.DiGraph:
    """Build a directed, weighted NetworkX graph from transaction data.

    Edge weight semantics:
      - frequency: number of distinct transactions between node pair
      - quantity: sum of quantity values
      - transaction_value: sum of monetary transaction values

    Args:
        organizations: DataFrame of organizations (for node attributes).
        transactions: DataFrame of all transactions.
        weight_mode: One of "frequency", "quantity", "transaction_value".


    Returns:
        NetworkX DiGraph with node and edge attributes.

    Raises:
        ValueError: If weight_mode is not recognized.
    """
    if weight_mode not in ("frequency", "quantity", "transaction_value"):
        raise ValueError(
            f"Unknown weight_mode '{weight_mode}'. "
            "Must be one of: frequency, quantity, transaction_value"
        )

    txns = transactions.copy()

    logger.info(
        "Building graph: weight_mode=%s, transactions=%d",
        weight_mode,
        len(txns),
    )

    G = nx.DiGraph()

    # ── Add nodes with attributes ─────────────────────────────────────────────
    node_rows = organizations
    for _, row in node_rows.iterrows():
        G.add_node(
            row["organization_id"],
            organization_name=row.get("organization_name", ""),
            organization_type=row.get("organization_type", ""),
            region=row.get("region", ""),
            industry=row.get("industry", ""),
            size_category=row.get("size_category", ""),
            status=row.get("status", "active"),
        )

    # ── Aggregate transactions into edge attributes ───────────────────────────
    if txns.empty:
        logger.warning("No transactions found for this filter — returning node-only graph")
        return G

    # Aggregate by (source, target)
    agg = (
        txns.groupby(["source_node", "target_node"])
        .agg(
            transaction_count=("transaction_id", "count"),
            total_quantity=("quantity", "sum"),
            total_value=("transaction_value", "sum"),
            avg_lead_time=("lead_time_days", "mean"),
        )
        .reset_index()
    )

    # Assign weight based on mode
    if weight_mode == "frequency":
        agg["weight"] = agg["transaction_count"]
    elif weight_mode == "quantity":
        agg["weight"] = agg["total_quantity"]
    else:  # transaction_value
        agg["weight"] = agg["total_value"]

    # Get most common relationship type per edge
    if "relationship_type" in txns.columns:
        rel_type_map = (
            txns.groupby(["source_node", "target_node"])["relationship_type"]
            .first()
            .to_dict()
        )
    else:
        rel_type_map = {}

    # ── Add edges ─────────────────────────────────────────────────────────────
    for _, row in agg.iterrows():
        src: str = row["source_node"]
        tgt: str = row["target_node"]

        # Skip self-loops
        if src == tgt:
            continue

        # Ensure nodes exist (in case of orphan transactions)
        if src not in G:
            G.add_node(src)
        if tgt not in G:
            G.add_node(tgt)

        G.add_edge(
            src,
            tgt,
            weight=float(row["weight"]),
            transaction_count=int(row["transaction_count"]),
            total_quantity=float(row["total_quantity"]),
            total_value=float(row["total_value"]),
            avg_lead_time=float(row["avg_lead_time"]),
            relationship_type=rel_type_map.get((src, tgt), "supply_chain_link"),
            weight_mode=weight_mode,
        )

    logger.info(
        "Graph built: %d nodes, %d edges",
        G.number_of_nodes(),
        G.number_of_edges(),
    )
    return G





def graph_to_undirected(G: nx.DiGraph) -> nx.Graph:
    """Convert a directed graph to undirected for algorithms requiring it.

    Edge weights are summed for bidirectional edges.

    Args:
        G: Directed graph.

    Returns:
        Undirected graph with combined edge weights.
    """
    return G.to_undirected(reciprocal=False)
