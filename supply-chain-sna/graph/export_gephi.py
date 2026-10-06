"""
Supply Chain SNA — Gephi Export
Writes the supply-chain graph as a GEXF file that Gephi opens directly.

Every node carries its organization attributes plus the centrality scores,
detected community, core number and planted role computed by this project,
so Gephi can colour and size nodes without recomputing anything, and its own
statistics can be compared against these columns.

CLI usage:
    python -m graph.export_gephi
    python -m graph.export_gephi --config config/default.yaml --output data/exports
"""
from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

CENTRALITY_COLUMNS = [
    "in_degree", "out_degree", "total_degree", "betweenness", "closeness",
    "eigenvector", "pagerank", "pagerank_reversed",
]


def build_export_graph(
    G: nx.DiGraph,
    centrality_df: pd.DataFrame,
    community_df: pd.DataFrame,
    kcore_df: pd.DataFrame,
    ground_truth: dict[str, Any],
) -> nx.DiGraph:
    """Return a copy of G with analysis results attached as node attributes.

    Args:
        G: Directed supply-chain graph.
        centrality_df: Combined centrality DataFrame.
        community_df: Community assignment DataFrame.
        kcore_df: K-core DataFrame.
        ground_truth: Ground-truth dictionary with planted structures.

    Returns:
        Graph whose node and edge attributes are all GEXF-safe scalars.
    """
    H = nx.DiGraph()

    centrality = centrality_df.set_index("node") if not centrality_df.empty else pd.DataFrame()
    community = dict(zip(community_df["node"], community_df["community_id"])) if not community_df.empty else {}
    core = dict(zip(kcore_df["node"], kcore_df["core_number"])) if not kcore_df.empty else {}

    hubs = set(ground_truth.get("planted_hubs", []))
    bridges = set(ground_truth.get("planted_bridges", []))
    critical_suppliers = {g["critical_supplier"] for g in ground_truth.get("planted_dependency_groups", [])}
    dependents = {
        m for g in ground_truth.get("planted_dependency_groups", []) for m in g["dependent_manufacturers"]
    }

    for node, data in G.nodes(data=True):
        attrs: dict[str, Any] = {
            "label": str(data.get("organization_name", "") or node),
            "organization_type": str(data.get("organization_type", "")),
            "region": str(data.get("region", "")),
            "industry": str(data.get("industry", "")),
            "size_category": str(data.get("size_category", "")),
            "status": str(data.get("status", "")),
        }
        if node in getattr(centrality, "index", []):
            row = centrality.loc[node]
            for col in CENTRALITY_COLUMNS:
                if col in row.index:
                    value = row[col]
                    attrs[f"nx_{col}"] = int(value) if col.endswith("degree") else float(value)
        if node in community:
            attrs["nx_community"] = int(community[node])
        if node in core:
            attrs["nx_core_number"] = int(core[node])
        attrs["planted_role"] = (
            "hub" if node in hubs
            else "bridge" if node in bridges
            else "critical_supplier" if node in critical_suppliers
            else "dependent_manufacturer" if node in dependents
            else "none"
        )
        H.add_node(node, **attrs)

    for u, v, data in G.edges(data=True):
        H.add_edge(
            u, v,
            weight=float(data.get("weight", 1.0)),
            transaction_count=int(data.get("transaction_count", 0)),
            total_quantity=float(data.get("total_quantity", 0.0)),
            total_value=float(data.get("total_value", 0.0)),
            relationship_type=str(data.get("relationship_type", "")),
        )
    return H


def main(argv: list[str] | None = None) -> None:
    """Export the graph and node table for Gephi.

    Args:
        argv: Optional CLI arguments for testing.
    """
    parser = argparse.ArgumentParser(description="Supply Chain SNA — Gephi Export")
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--output", default="data/exports", help="Output directory")
    args = parser.parse_args(argv)

    from config import load_config
    config = load_config(args.config)

    data_dir = Path(config["output"]["data_dir"])
    graph_dir = Path(config["output"]["graph_dir"])
    results_dir = Path(config["output"]["results_dir"])
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = graph_dir / "supply_chain_graph_frequency.pkl"
    if not graph_path.exists():
        logger.error("Graph not found. Run: python -m graph.build")
        sys.exit(1)
    with graph_path.open("rb") as fh:
        G = pickle.load(fh)

    def load_csv(name: str) -> pd.DataFrame:
        p = results_dir / name
        return pd.read_csv(p) if p.exists() else pd.DataFrame()

    centrality_df = load_csv("centrality.csv")
    if centrality_df.empty:
        logger.warning("No centrality results found. Run experiments first to include them in the export.")

    gt_path = data_dir / "ground_truth.json"
    ground_truth = json.loads(gt_path.read_text()) if gt_path.exists() else {}

    H = build_export_graph(G, centrality_df, load_csv("communities.csv"), load_csv("kcore.csv"), ground_truth)

    gexf_path = out_dir / "supply_chain.gexf"
    nx.write_gexf(H, gexf_path)
    logger.info("Saved GEXF → %s (%d nodes, %d edges)", gexf_path, H.number_of_nodes(), H.number_of_edges())

    nodes_path = out_dir / "gephi_nodes.csv"
    pd.DataFrame(
        [{"Id": n, **d} for n, d in H.nodes(data=True)]
    ).to_csv(nodes_path, index=False)
    logger.info("Saved node table → %s", nodes_path)


if __name__ == "__main__":
    main()
