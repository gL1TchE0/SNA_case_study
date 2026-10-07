"""
Supply Chain SNA — Main Generator Entry Point
PHASE 0/1/2/3/4: Orchestrates the full data generation pipeline.

CLI usage:
    python -m generator.generate --config config/default.yaml
    python -m generator.generate --config config/smoke.yaml --seed 99
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the data generator.

    Args:
        argv: Optional list of CLI arguments (for testing).
    """
    parser = argparse.ArgumentParser(description="Supply Chain SNA — Data Generator")
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override random seed from config",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override output directory",
    )
    args = parser.parse_args(argv)

    # ── Load configuration ────────────────────────────────────────────────────
    from config import load_config, merge_config

    config = load_config(args.config)

    if args.seed is not None:
        config = merge_config(config, {"seed": args.seed})

    if args.output is not None:
        config["output"]["data_dir"] = args.output

    # ── Set up output directories ─────────────────────────────────────────────
    output_dir = Path(config["output"]["data_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Run generation (covers Phases 1–3) ───────────────────────────
    logger.info("=== Starting Supply Chain Data Generation ===")
    logger.info("Config: %s, Seed: %d", args.config, config["seed"])

    from generator.organization_generator import generate_organizations
    from generator.network_generator import generate_network
    from generator.transaction_generator import generate_transactions

    organizations, ground_truth = generate_organizations(config)
    edges_df, ground_truth = generate_network(organizations, ground_truth, config)
    transactions = generate_transactions(edges_df, organizations, config)

    # ── Save outputs ──────────────────────────────────────────────────────────
    orgs_path = output_dir / "organizations.csv"
    txns_path = output_dir / "transactions.csv"
    gt_path = output_dir / "ground_truth.json"
    meta_path = output_dir / "dataset_metadata.json"

    organizations.to_csv(orgs_path, index=False)
    logger.info("Saved organizations → %s (%d rows)", orgs_path, len(organizations))

    transactions.to_csv(txns_path, index=False)
    logger.info("Saved transactions → %s (%d rows)", txns_path, len(transactions))

    # Convert ground_truth to JSON-serializable form
    gt_json = _serialize_ground_truth(ground_truth)
    with gt_path.open("w") as fh:
        json.dump(gt_json, fh, indent=2)
    logger.info("Saved ground truth → %s", gt_path)

    # ── Save dataset metadata ─────────────────────────────────────────────────
    metadata: dict[str, Any] = {
        "dataset_id": f"dataset-{config['seed']}-{config['dataset_version']}",
        "seed": config["seed"],
        "dataset_version": config["dataset_version"],
        "generator_version": config["generator_version"],
        "generation_timestamp": datetime.utcnow().isoformat() + "Z",
        "config_path": str(args.config),
        "network_size": len(organizations),
        "edge_count": transactions[["source_node", "target_node"]].drop_duplicates().shape[0],
        "transaction_count": len(transactions),
        "time_range": {
            "start": config["network"]["start_date"],
            "months": config["network"]["months"],
        },
        "organization_type_counts": organizations["organization_type"].value_counts().to_dict(),
        "regions": config["regions"],
        "planted_hubs": len(ground_truth.get("planted_hubs", [])),
        "planted_bridges": len(ground_truth.get("planted_bridges", [])),
        "planted_communities": len(ground_truth.get("planted_communities", {})),
        "planted_dependency_groups": len(ground_truth.get("planted_dependency_groups", [])),
    }

    with meta_path.open("w") as fh:
        json.dump(metadata, fh, indent=2)
    logger.info("Saved metadata → %s", meta_path)

    logger.info("=== Generation Complete ===")
    logger.info(
        "Organizations: %d | Transactions: %d | Unique Edges: %d | Months: %d",
        metadata["network_size"],
        metadata["transaction_count"],
        metadata["edge_count"],
        config["network"]["months"],
    )


def _serialize_ground_truth(gt: dict[str, Any]) -> dict[str, Any]:
    """Convert ground truth dict to JSON-serializable format.

    Args:
        gt: Ground truth dictionary (may contain non-JSON types).

    Returns:
        JSON-serializable dictionary.
    """
    result: dict[str, Any] = {}
    for key, value in gt.items():
        if isinstance(value, dict):
            result[key] = {str(k): _make_json_safe(v) for k, v in value.items()}
        elif isinstance(value, list):
            result[key] = [_make_json_safe(v) for v in value]
        else:
            result[key] = _make_json_safe(value)
    return result


def _make_json_safe(obj: Any) -> Any:
    """Recursively convert an object to JSON-safe types.

    Args:
        obj: Object to convert.

    Returns:
        JSON-safe version of the object.
    """
    if isinstance(obj, dict):
        return {str(k): _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_make_json_safe(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj


if __name__ == "__main__":
    main()
