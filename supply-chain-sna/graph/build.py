"""
Supply Chain SNA — Graph Build Entry Point
PHASE 6: CLI for loading data and building graphs.

CLI usage:
    python -m graph.build
    python -m graph.build --config config/default.yaml
"""
from __future__ import annotations

import argparse
import logging
import pickle
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Build the supply-chain graph from generated data.

    Args:
        argv: Optional CLI arguments for testing.
    """
    parser = argparse.ArgumentParser(description="Supply Chain SNA — Graph Builder")
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--weight-mode", default="frequency",
                        choices=["frequency", "quantity", "transaction_value"])
    args = parser.parse_args(argv)

    from config import load_config
    config = load_config(args.config)

    data_dir = Path(config["output"]["data_dir"])
    graph_dir = Path(config["output"]["graph_dir"])
    graph_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    orgs_path = data_dir / "organizations.csv"
    txns_path = data_dir / "transactions.csv"

    if not orgs_path.exists() or not txns_path.exists():
        logger.error("Data files not found. Run generator first: python -m generator.generate")
        sys.exit(1)

    organizations = pd.read_csv(orgs_path)
    transactions = pd.read_csv(txns_path)
    logger.info("Loaded %d organizations, %d transactions", len(organizations), len(transactions))

    # Run validation
    from graph.validation import validate_dataset, save_validation_report
    report = validate_dataset(organizations, transactions)
    save_validation_report(report, data_dir / "data_quality_report.json")

    if not report["is_valid"]:
        logger.error("Data validation failed. See data_quality_report.json")
        sys.exit(1)

    # Build full graph
    from graph.builder import build_graph, build_temporal_graphs

    weight_mode = args.weight_mode
    G = build_graph(organizations, transactions, weight_mode=weight_mode)

    # Save graph
    graph_path = graph_dir / f"supply_chain_graph_{weight_mode}.pkl"
    with graph_path.open("wb") as fh:
        pickle.dump(G, fh)
    logger.info("Saved graph → %s (%d nodes, %d edges)", graph_path, G.number_of_nodes(), G.number_of_edges())

    # Build temporal graphs
    snapshot_mode = config.get("snapshots", {}).get("mode", "monthly")
    temporal_graphs = build_temporal_graphs(
        organizations, transactions, weight_mode=weight_mode, mode=snapshot_mode
    )
    temporal_path = graph_dir / f"temporal_graphs_{weight_mode}.pkl"
    with temporal_path.open("wb") as fh:
        pickle.dump(temporal_graphs, fh)
    logger.info("Saved temporal graphs → %s (%d months)", temporal_path, len(temporal_graphs))

    logger.info("=== Graph Build Complete ===")


if __name__ == "__main__":
    main()
