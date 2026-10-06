"""
Supply Chain SNA — Centrality Analysis Orchestrator
PHASE 8/9: Runs all centrality analyses and builds comparison table.

Computes degree, betweenness, closeness, eigenvector, and PageRank.
Generates rank correlation analysis and identifies nodes with divergent
centrality profiles.
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

from sna.degree import compute_degree
from sna.betweenness import compute_betweenness
from sna.closeness import compute_closeness
from sna.eigenvector import compute_eigenvector
from sna.pagerank import compute_pagerank

logger = logging.getLogger(__name__)


def compute_all_centrality(
    G: nx.DiGraph,
    config: dict[str, Any] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compute all centrality metrics and build a comparison table.

    Args:
        G: Directed supply-chain graph.
        config: Optional configuration dictionary for centrality parameters.

    Returns:
        Tuple of:
            - Combined centrality DataFrame (node, degree metrics, betweenness,
              closeness, eigenvector, pagerank, plus ranks for each)
            - Statistics dictionary with rank correlations
    """
    if config is None:
        config = {}
    centrality_cfg = config.get("centrality", {})

    # ── Compute each metric ───────────────────────────────────────────────────
    logger.info("Computing all centrality metrics…")

    degree_df = compute_degree(G)
    betweenness_df = compute_betweenness(
        G,
        normalized=centrality_cfg.get("betweenness_normalized", True),
    )
    closeness_df = compute_closeness(G)
    eigenvector_df = compute_eigenvector(
        G,
        max_iter=centrality_cfg.get("eigenvector_max_iter", 1000),
        tol=centrality_cfg.get("eigenvector_tol", 1e-6),
    )
    pagerank_df = compute_pagerank(
        G,
        alpha=centrality_cfg.get("pagerank_alpha", 0.85),
        max_iter=centrality_cfg.get("pagerank_max_iter", 1000),
        tol=centrality_cfg.get("pagerank_tol", 1e-6),
    )

    # PageRank on the reversed graph. Standard PageRank flows downstream and
    # rewards sinks (retailers); reversing the edges rewards organizations
    # that many others ultimately draw supply from (upstream importance).
    pagerank_rev_df = compute_pagerank(
        G.reverse(copy=True),
        alpha=centrality_cfg.get("pagerank_alpha", 0.85),
        max_iter=centrality_cfg.get("pagerank_max_iter", 1000),
        tol=centrality_cfg.get("pagerank_tol", 1e-6),
    ).rename(columns={"pagerank": "pagerank_reversed"})

    # ── Merge into combined table ─────────────────────────────────────────────
    combined = degree_df[["node", "in_degree", "out_degree", "total_degree",
                           "in_degree_centrality", "out_degree_centrality"]].copy()
    combined = combined.merge(
        betweenness_df[["node", "betweenness"]], on="node", how="left"
    )
    combined = combined.merge(
        closeness_df[["node", "closeness"]], on="node", how="left"
    )
    combined = combined.merge(
        eigenvector_df[["node", "eigenvector"]], on="node", how="left"
    )
    combined = combined.merge(
        pagerank_df[["node", "pagerank"]], on="node", how="left"
    )

    combined = combined.merge(
        pagerank_rev_df[["node", "pagerank_reversed"]], on="node", how="left"
    )

    # ── Compute ranks ─────────────────────────────────────────────────────────
    for metric in ["total_degree", "betweenness", "closeness", "eigenvector", "pagerank", "pagerank_reversed"]:
        if metric in combined.columns:
            combined[f"{metric}_rank"] = combined[metric].rank(
                ascending=False, method="min", na_option="bottom"
            ).astype(int)

    combined = combined.fillna(0.0)

    # ── Rank correlation analysis ─────────────────────────────────────────────
    rank_cols = [c for c in combined.columns if c.endswith("_rank")]
    corr_results: dict[str, float] = {}

    metric_pairs = [
        ("total_degree_rank", "betweenness_rank"),
        ("total_degree_rank", "pagerank_rank"),
        ("betweenness_rank", "pagerank_rank"),
        ("eigenvector_rank", "pagerank_rank"),
        ("betweenness_rank", "closeness_rank"),
        ("total_degree_rank", "pagerank_reversed_rank"),
        ("pagerank_rank", "pagerank_reversed_rank"),
    ]

    for col_a, col_b in metric_pairs:
        if col_a in combined.columns and col_b in combined.columns:
            corr, pval = scipy_stats.spearmanr(combined[col_a], combined[col_b])
            key = f"{col_a.replace('_rank','')}_vs_{col_b.replace('_rank','')}"
            corr_results[key] = {"spearman_r": float(corr), "p_value": float(pval)}

    # ── Identify divergent nodes ──────────────────────────────────────────────
    # Nodes ranked far better on betweenness than on degree (bridge despite
    # modest connectivity): large positive total_degree_rank - betweenness_rank.
    if "betweenness_rank" in combined.columns and "total_degree_rank" in combined.columns:
        combined["bridge_without_hub"] = (
            combined["total_degree_rank"] - combined["betweenness_rank"]
        )
        true_bridges = combined.nlargest(10, "bridge_without_hub")[["node", "bridge_without_hub", "betweenness", "total_degree"]]
    else:
        true_bridges = pd.DataFrame()

    stats: dict[str, Any] = {
        "rank_correlations": corr_results,
        "top_by_degree": combined.nsmallest(10, "total_degree_rank")["node"].tolist(),
        "top_by_betweenness": combined.nsmallest(10, "betweenness_rank")["node"].tolist(),
        "top_by_pagerank": combined.nsmallest(10, "pagerank_rank")["node"].tolist(),
        "top_by_pagerank_reversed": combined.nsmallest(10, "pagerank_reversed_rank")["node"].tolist(),
        "weighting_note": (
            "PageRank and eigenvector use edge weights (transaction frequency). "
            "Degree, betweenness and closeness are unweighted: frequency is a "
            "strength, not a distance, so it is not used as a path cost."
        ),
        "bridge_without_hub_nodes": true_bridges.to_dict("records") if not true_bridges.empty else [],
    }

    logger.info("Centrality comparison table built: %d nodes, %d metrics", len(combined), 6)
    return combined, stats
