"""
Supply Chain SNA — Ground-Truth Experiments
PHASE 15: Evaluates whether SNA algorithms recover planted structures.

Experiments:
  A. Hub recovery: Does high degree/PageRank identify planted hubs?
  B. Bridge recovery: Does high betweenness identify planted bridges?
  C. Community recovery: Does community detection recover planted communities?
  D. Dependency recovery: Does dependency analysis find planted dep groups?
  E. Critical node resilience: Does removing planted critical nodes degrade the network?
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)


def run_ground_truth_experiments(
    G: nx.DiGraph,
    centrality_df: pd.DataFrame,
    community_df: pd.DataFrame,
    ground_truth: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run all ground-truth evaluation experiments.

    Args:
        G: Directed supply-chain graph.
        centrality_df: Combined centrality DataFrame.
        community_df: Community assignment DataFrame.
        ground_truth: Ground truth dictionary with planted structures.
        config: Optional configuration dictionary.

    Returns:
        Dictionary with results for each experiment (A through E).
    """
    results: dict[str, Any] = {}

    # ── Experiment A: Hub recovery ────────────────────────────────────────────
    results["experiment_A_hub_recovery"] = _hub_recovery(
        centrality_df, ground_truth.get("planted_hubs", [])
    )

    # ── Experiment B: Bridge recovery ─────────────────────────────────────────
    results["experiment_B_bridge_recovery"] = _bridge_recovery(
        centrality_df, ground_truth.get("planted_bridges", [])
    )

    # ── Experiment C: Community recovery ─────────────────────────────────────
    planted_communities = ground_truth.get("planted_communities", {})
    if planted_communities and not community_df.empty:
        from sna.communities import evaluate_community_recovery
        try:
            comm_eval = evaluate_community_recovery(community_df, planted_communities)
        except ImportError:
            comm_eval = {"ari": None, "nmi": None, "note": "sklearn not available for evaluation"}
        results["experiment_C_community_recovery"] = comm_eval
    else:
        results["experiment_C_community_recovery"] = {
            "ari": None, "nmi": None, "note": "No planted communities or community data available"
        }

    # ── Experiment D: Dependency recovery ────────────────────────────────────
    results["experiment_D_dependency_recovery"] = _dependency_recovery(
        G, centrality_df, ground_truth.get("planted_dependency_groups", [])
    )

    # ── Experiment E: Critical node resilience ────────────────────────────────
    results["experiment_E_critical_node_resilience"] = _critical_node_resilience(
        G, ground_truth.get("planted_hubs", [])
    )

    logger.info("Ground-truth experiments complete")
    return results


def _hub_recovery(
    centrality_df: pd.DataFrame,
    planted_hubs: list[str],
    top_n: int = 20,
) -> dict[str, Any]:
    """Check whether planted hubs appear in top-N centrality rankings.

    Args:
        centrality_df: Combined centrality DataFrame.
        planted_hubs: List of planted hub node IDs.
        top_n: Number of top nodes to check.

    Returns:
        Evaluation dictionary with recovery metrics.
    """
    if not planted_hubs or centrality_df.empty:
        return {"note": "No planted hubs or centrality data available"}

    results: dict[str, Any] = {
        "planted_hubs": planted_hubs,
        "top_n": top_n,
    }

    for metric in ["total_degree", "pagerank", "pagerank_reversed", "betweenness"]:
        if f"{metric}_rank" not in centrality_df.columns:
            continue
        top_nodes = centrality_df.nsmallest(top_n, f"{metric}_rank")["node"].tolist()
        recovered = [h for h in planted_hubs if h in top_nodes]
        results[f"recovered_by_{metric}"] = recovered
        results[f"recovery_rate_{metric}"] = len(recovered) / max(1, len(planted_hubs))

    return results


def _bridge_recovery(
    centrality_df: pd.DataFrame,
    planted_bridges: list[str],
    top_n: int = 30,
) -> dict[str, Any]:
    """Check whether planted bridges appear in top-N betweenness rankings.

    Args:
        centrality_df: Combined centrality DataFrame.
        planted_bridges: List of planted bridge node IDs.
        top_n: Number of top nodes to check.

    Returns:
        Evaluation dictionary.
    """
    if not planted_bridges or centrality_df.empty:
        return {"note": "No planted bridges or centrality data available"}

    if "betweenness_rank" not in centrality_df.columns:
        return {"note": "Betweenness not computed"}

    top_by_betweenness = centrality_df.nsmallest(top_n, "betweenness_rank")["node"].tolist()
    recovered = [b for b in planted_bridges if b in top_by_betweenness]

    bridge_rows = centrality_df[centrality_df["node"].isin(planted_bridges)]
    bridge_ranks = {
        row["node"]: {
            "betweenness_rank": int(row["betweenness_rank"]),
            "total_degree_rank": int(row["total_degree_rank"]),
        }
        for _, row in bridge_rows.iterrows()
    }

    return {
        "planted_bridges": planted_bridges,
        "top_n": top_n,
        "recovered_bridges": recovered,
        "recovery_rate": len(recovered) / max(1, len(planted_bridges)),
        "median_betweenness_rank": float(bridge_rows["betweenness_rank"].median()) if not bridge_rows.empty else None,
        "median_total_degree_rank": float(bridge_rows["total_degree_rank"].median()) if not bridge_rows.empty else None,
        "bridge_ranks": bridge_ranks,
        "note": f"{len(recovered)}/{len(planted_bridges)} planted bridges found in top-{top_n} betweenness",
    }


def _dependency_recovery(
    G: nx.DiGraph,
    centrality_df: pd.DataFrame,
    dependency_groups: list[dict[str, Any]],
    top_fraction: float = 0.10,
) -> dict[str, Any]:
    """Check whether dependency analysis exposes the planted dependency groups.

    The generator plants one critical supplier per group and routes extra
    volume from it to several manufacturers. Nothing in the analysis is told
    which edges were planted. Two things are tested:

      1. Manufacturer side: does the dependency analysis name the planted
         supplier as each manufacturer's top supplier, and is that
         manufacturer's dependency ratio in the top ``top_fraction`` of all
         manufacturers?
      2. Supplier side: is the critical supplier in the top ``top_fraction``
         of suppliers by reversed PageRank (upstream importance) and by
         weighted out-degree?

    Args:
        G: Directed graph.
        centrality_df: Centrality DataFrame.
        dependency_groups: List of planted dependency group dicts.
        top_fraction: Fraction defining "highly ranked".

    Returns:
        Evaluation dictionary.
    """
    if not dependency_groups:
        return {"note": "No planted dependency groups"}

    from sna.dependencies import analyze_dependencies

    conc = analyze_dependencies(G)["upstream_concentration"]
    if conc.empty:
        return {"note": "No dependency data available"}

    mfg_conc = conc[conc["node_type"] == "manufacturer"].set_index("node")
    ratio_threshold = float(mfg_conc["supplier_dependency_ratio"].quantile(1 - top_fraction))

    suppliers = [n for n, d in G.nodes(data=True) if d.get("organization_type") == "supplier"]
    out_strength = pd.Series({n: G.out_degree(n, weight="weight") for n in suppliers})
    strength_rank = out_strength.rank(ascending=False, method="min")
    rev_pr = pd.Series(dtype=float)
    if not centrality_df.empty and "pagerank_reversed" in centrality_df.columns:
        rev_pr = centrality_df.set_index("node")["pagerank_reversed"].reindex(suppliers)
    rev_pr_rank = rev_pr.rank(ascending=False, method="min")
    supplier_cutoff = max(1, round(len(suppliers) * top_fraction))

    results: list[dict[str, Any]] = []
    for group in dependency_groups:
        supplier = group.get("critical_supplier")
        manufacturers = group.get("dependent_manufacturers", [])
        if not supplier or not manufacturers:
            continue

        named = [
            m for m in manufacturers
            if m in mfg_conc.index and mfg_conc.loc[m, "top_supplier"] == supplier
        ]
        flagged = [
            m for m in named
            if mfg_conc.loc[m, "supplier_dependency_ratio"] >= ratio_threshold
        ]
        ratios = [
            float(mfg_conc.loc[m, "supplier_dependency_ratio"])
            for m in manufacturers if m in mfg_conc.index
        ]

        s_rank = int(strength_rank[supplier]) if supplier in strength_rank.index else None
        p_rank = int(rev_pr_rank[supplier]) if supplier in rev_pr_rank.index and pd.notna(rev_pr_rank[supplier]) else None

        results.append(
            {
                "group_id": group.get("group_id"),
                "critical_supplier": supplier,
                "planted_manufacturers": len(manufacturers),
                "top_supplier_identified": len(named),
                "flagged_high_dependency": len(flagged),
                "mean_dependency_ratio": round(sum(ratios) / max(1, len(ratios)), 4),
                "supplier_out_strength_rank": s_rank,
                "supplier_pagerank_reversed_rank": p_rank,
                "supplier_in_top_by_out_strength": s_rank is not None and s_rank <= supplier_cutoff,
                "supplier_in_top_by_pagerank_reversed": p_rank is not None and p_rank <= supplier_cutoff,
            }
        )

    total_planted = sum(r["planted_manufacturers"] for r in results)
    return {
        "dependency_group_results": results,
        "top_fraction": top_fraction,
        "manufacturer_ratio_threshold": round(ratio_threshold, 4),
        "population_mean_manufacturer_ratio": round(float(mfg_conc["supplier_dependency_ratio"].mean()), 4),
        "num_suppliers_ranked": len(suppliers),
        "top_supplier_identification_rate": sum(r["top_supplier_identified"] for r in results) / max(1, total_planted),
        "high_dependency_flag_rate": sum(r["flagged_high_dependency"] for r in results) / max(1, total_planted),
        "critical_suppliers_in_top_by_out_strength": sum(r["supplier_in_top_by_out_strength"] for r in results),
        "critical_suppliers_in_top_by_pagerank_reversed": sum(r["supplier_in_top_by_pagerank_reversed"] for r in results),
    }


def _critical_node_resilience(
    G: nx.DiGraph,
    critical_nodes: list[str],
) -> dict[str, Any]:
    """Measure network degradation after removing planted critical nodes.

    Args:
        G: Original directed graph.
        critical_nodes: Planted critical (hub) node IDs.

    Returns:
        Comparison of before/after network metrics.
    """
    if not critical_nodes:
        return {"note": "No critical nodes to remove"}

    # Baseline
    wcc_before = list(nx.weakly_connected_components(G))
    lcc_before = max(len(c) for c in wcc_before) if wcc_before else 0
    U_before = G.to_undirected()
    eff_before = nx.global_efficiency(U_before) if U_before.number_of_nodes() > 0 else 0.0

    # Remove critical nodes
    H = G.copy()
    actually_removed = [n for n in critical_nodes if n in H]
    H.remove_nodes_from(actually_removed)

    wcc_after = list(nx.weakly_connected_components(H))
    lcc_after = max(len(c) for c in wcc_after) if wcc_after else 0
    U_after = H.to_undirected()
    eff_after = nx.global_efficiency(U_after) if U_after.number_of_nodes() > 0 else 0.0

    n = G.number_of_nodes()
    return {
        "nodes_removed": len(actually_removed),
        "fraction_removed": len(actually_removed) / max(1, n),
        "lcc_before": lcc_before,
        "lcc_after": lcc_after,
        "lcc_fraction_before": lcc_before / max(1, n),
        "lcc_fraction_after": lcc_after / max(1, H.number_of_nodes() + len(actually_removed)),
        "lcc_change": lcc_after - lcc_before,
        "efficiency_before": eff_before,
        "efficiency_after": eff_after,
        "efficiency_change": eff_after - eff_before,
        "components_before": len(wcc_before),
        "components_after": len(wcc_after),
    }
