"""
Supply Chain SNA — Research Report Generator
PHASE 22: Generates research summary from actual experiment outputs.

CLI usage:
    python -m reports.generate
    python -m reports.generate --config config/default.yaml
"""
from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Generate research reports and figures.

    Args:
        argv: Optional CLI arguments for testing.
    """
    parser = argparse.ArgumentParser(description="Supply Chain SNA — Report Generator")
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args(argv)

    from config import load_config
    config = load_config(args.config)

    data_dir = Path(config["output"]["data_dir"])
    graph_dir = Path(config["output"]["graph_dir"])
    results_dir = Path(config["output"]["results_dir"])
    figures_dir = Path(config["output"]["figures_dir"])
    tables_dir = Path(config["output"]["tables_dir"])

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Load graph
    graph_path = graph_dir / "supply_chain_graph_frequency.pkl"
    if not graph_path.exists():
        logger.error("Graph not found. Run graph.build and experiments.run first.")
        sys.exit(1)

    with graph_path.open("rb") as fh:
        G = pickle.load(fh)

    # Load result files
    def load_csv(name: str) -> pd.DataFrame:
        p = results_dir / name
        return pd.read_csv(p) if p.exists() else pd.DataFrame()

    def load_json(name: str) -> dict[str, Any]:
        p = results_dir / name
        if p.exists():
            with p.open() as fh:
                return json.load(fh)
        return {}

    centrality_df = load_csv("centrality.csv")
    community_df = load_csv("communities.csv")
    kcore_df = load_csv("kcore.csv")
    dep_df = load_csv("dependencies.csv")
    snapshot_df = load_csv("temporal.csv")
    net_stats = load_json("network_statistics.json")
    comm_stats = load_json("community_stats.json")
    gt_results = load_json("ground_truth_results.json")
    cent_stats = load_json("centrality_stats.json")
    summary = load_json("summary.json")

    gt_path = data_dir / "ground_truth.json"
    ground_truth: dict[str, Any] = {}
    if gt_path.exists():
        with gt_path.open() as fh:
            ground_truth = json.load(fh)

    # Load resilience results
    resilience_results: dict[str, pd.DataFrame] = {}
    for strategy in ["random", "degree", "betweenness", "pagerank"]:
        df = load_csv(f"resilience_{strategy}.csv")
        if not df.empty:
            resilience_results[strategy] = df

    # ── Generate figures ──────────────────────────────────────────────────────
    logger.info("Generating figures…")
    from reports.visualization import generate_all_figures
    generate_all_figures(
        G=G,
        centrality_df=centrality_df,
        community_df=community_df,
        snapshot_df=snapshot_df,
        resilience_results=resilience_results,
        figures_dir=figures_dir,
        kcore_df=kcore_df,
        dep_df=dep_df,
        ground_truth=ground_truth,
    )

    # ── Generate tables ───────────────────────────────────────────────────────
    logger.info("Generating tables…")
    _generate_tables(centrality_df, community_df, kcore_df, dep_df, tables_dir)

    # ── Generate summary markdown ─────────────────────────────────────────────
    logger.info("Generating research summary…")
    summary_md = _generate_summary_markdown(
        net_stats=net_stats,
        cent_stats=cent_stats,
        centrality_df=centrality_df,
        comm_stats=comm_stats,
        community_df=community_df,
        dep_df=dep_df,
        snapshot_df=snapshot_df,
        resilience_results=resilience_results,
        gt_results=gt_results,
        config=config,
    )

    summary_path = Path(config["output"]["reports_dir"]) / "summary.md"
    with summary_path.open("w") as fh:
        fh.write(summary_md)
    logger.info("Summary → %s", summary_path)
    logger.info("=== Report Generation Complete ===")


def _generate_tables(
    centrality_df: pd.DataFrame,
    community_df: pd.DataFrame,
    kcore_df: pd.DataFrame,
    dep_df: pd.DataFrame,
    tables_dir: Path,
) -> None:
    """Generate CSV tables for research report.

    Args:
        centrality_df: Centrality DataFrame.
        community_df: Community DataFrame.
        kcore_df: K-core DataFrame.
        dep_df: Dependency concentration DataFrame.
        tables_dir: Output directory.
    """
    if not centrality_df.empty:
        # Top 20 by each metric
        for metric in ["total_degree", "betweenness", "pagerank", "pagerank_reversed", "closeness"]:
            if metric in centrality_df.columns:
                top = centrality_df.nlargest(20, metric)[
                    ["node"] + [m for m in ["in_degree", "out_degree", "total_degree",
                                            "betweenness", "pagerank", "pagerank_reversed", "closeness", "eigenvector"] if m in centrality_df.columns]
                ]
                top.to_csv(tables_dir / f"top20_{metric}.csv", index=False)

    if not community_df.empty:
        comm_sizes = community_df["community_id"].value_counts().reset_index()
        comm_sizes.columns = ["community_id", "size"]
        comm_sizes.to_csv(tables_dir / "community_sizes.csv", index=False)

    if not kcore_df.empty:
        kcore_df.to_csv(tables_dir / "kcore_decomposition.csv", index=False)

    if not dep_df.empty:
        dep_df.head(50).to_csv(tables_dir / "top50_dependencies.csv", index=False)


def _generate_summary_markdown(
    net_stats: dict,
    cent_stats: dict,
    centrality_df: pd.DataFrame,
    comm_stats: dict,
    community_df: pd.DataFrame,
    dep_df: pd.DataFrame,
    snapshot_df: pd.DataFrame,
    resilience_results: dict,
    gt_results: dict,
    config: dict,
) -> str:
    """Generate a markdown research summary from actual results.

    All values in the summary are derived from the actual experiment outputs.

    Args:
        net_stats: Network statistics dictionary.
        cent_stats: Centrality statistics dictionary.
        centrality_df: Centrality DataFrame.
        comm_stats: Community statistics.
        community_df: Community DataFrame.
        dep_df: Dependency DataFrame.
        snapshot_df: Temporal snapshot DataFrame.
        resilience_results: Resilience results per strategy.
        gt_results: Ground-truth experiment results.
        config: Configuration dictionary.

    Returns:
        Markdown string for the research summary.
    """
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    seed = config.get("seed", "N/A")

    lines = [
        "# Supply Chain Social Network Analysis — Research Summary",
        f"\n**Generated**: {ts}  ",
        f"**Seed**: {seed}  ",
        f"**Dataset Version**: {config.get('dataset_version', 'v1')}  ",
        "\n---\n",
        "## 1. Dataset Statistics\n",
    ]

    # Network stats
    if net_stats:
        lines += [
            f"- **Nodes**: {net_stats.get('num_nodes', 'N/A')}",
            f"- **Edges**: {net_stats.get('num_edges', 'N/A')}",
            f"- **Density**: {net_stats.get('density', 0):.6f}",
            f"- **Weakly Connected Components**: {net_stats.get('weakly_connected_components', 'N/A')}",
            f"- **Largest WCC Fraction**: {net_stats.get('largest_wcc_fraction', 0):.4f}",
            f"- **Average Total Degree**: {net_stats.get('avg_total_degree', 0):.2f}",
            f"- **Avg Clustering (undirected)**: {net_stats.get('avg_clustering_undirected', 0):.4f}",
            f"- **Global Efficiency**: {net_stats.get('global_efficiency', 'N/A')}",
        ]
    lines.append("\n---\n")

    # Centrality findings
    lines.append("## 2. Centrality Findings\n")
    if not centrality_df.empty:
        for metric in ["total_degree", "betweenness", "pagerank", "pagerank_reversed"]:
            if metric in centrality_df.columns:
                top3 = centrality_df.nlargest(3, metric)[["node", metric]]
                lines.append(f"### Top 3 by {metric.replace('_', ' ').title()}")
                for _, row in top3.iterrows():
                    lines.append(f"- {row['node']}: {row[metric]:.6f}")
        if cent_stats.get("rank_correlations"):
            lines.append("\n### Rank Correlations (Spearman)")
            for pair, corr_data in cent_stats["rank_correlations"].items():
                if isinstance(corr_data, dict):
                    lines.append(f"- {pair}: r = {corr_data.get('spearman_r', 0):.4f}")
    lines.append("\n---\n")

    # Community findings
    lines.append("## 3. Community Detection\n")
    if comm_stats:
        lines += [
            f"- **Algorithm**: {comm_stats.get('algorithm', 'N/A')}",
            f"- **Communities Detected**: {comm_stats.get('num_communities', 'N/A')}",
            f"- **Modularity**: {comm_stats.get('modularity', 'N/A')}",
            f"- **Inter-community Edge Fraction**: {comm_stats.get('inter_community_fraction', 0):.4f}",
        ]
    lines.append("\n---\n")

    # Dependency findings
    lines.append("## 4. Dependency Analysis\n")
    if not dep_df.empty and "supplier_dependency_ratio" in dep_df.columns:
        high_conc = dep_df[dep_df["supplier_dependency_ratio"] > 0.8]
        lines += [
            "- Logistics-provider edges are excluded from supplier counts",
            f"- **Nodes with >80% upstream concentration**: {len(high_conc)}",
            f"- **Mean supplier dependency ratio**: {dep_df['supplier_dependency_ratio'].mean():.4f}",
        ]
    lines.append("\n---\n")

    # Temporal findings
    lines.append("## 5. Temporal Analysis\n")
    if not snapshot_df.empty:
        lines += [
            f"- **Months analyzed**: {len(snapshot_df)}",
            f"- **Node count range**: {int(snapshot_df['num_nodes'].min())}–{int(snapshot_df['num_nodes'].max())}",
            f"- **Edge count range**: {int(snapshot_df['num_edges'].min())}–{int(snapshot_df['num_edges'].max())}",
            f"- **Density trend**: {snapshot_df.iloc[0]['density']:.6f} → {snapshot_df.iloc[-1]['density']:.6f}",
        ]
        if "num_communities" in snapshot_df.columns:
            lines.append(f"- **Detected communities per month**: {int(snapshot_df['num_communities'].min())}–{int(snapshot_df['num_communities'].max())}")
            lines.append(f"- **Modularity range**: {snapshot_df['modularity'].min():.4f}–{snapshot_df['modularity'].max():.4f}")
    lines.append("\n---\n")

    # Resilience findings
    lines.append("## 6. Resilience Findings\n")
    for strategy, df in resilience_results.items():
        if df.empty:
            continue
        col = "lcc_mean" if "lcc_mean" in df.columns else "largest_component_fraction"
        if col in df.columns and len(df) > 1:
            lcc_at_10 = df[df["fraction_removed"] >= 0.10].iloc[0][col] if len(df[df["fraction_removed"] >= 0.10]) > 0 else "N/A"
            lines.append(f"- **{strategy.title()} removal at 10%**: LCC = {lcc_at_10:.4f}" if lcc_at_10 != "N/A" else f"- **{strategy}**: no 10% data")
    lines.append("\n---\n")

    # Ground-truth evaluation
    lines.append("## 7. Ground-Truth Evaluation\n")
    if gt_results:
        exp_a = gt_results.get("experiment_A_hub_recovery", {})
        for metric in ["total_degree", "betweenness", "pagerank", "pagerank_reversed"]:
            rate = exp_a.get(f"recovery_rate_{metric}")
            if rate is not None:
                lines.append(f"- **Hub recovery in top-{exp_a.get('top_n')} by {metric}**: {rate:.2f}")
        exp_b = gt_results.get("experiment_B_bridge_recovery", {})
        if exp_b:
            lines.append(f"- **Bridge recovery in top-{exp_b.get('top_n')} betweenness**: {exp_b.get('recovery_rate', 'N/A')}")
            lines.append(f"- **Median betweenness rank of planted bridges**: {exp_b.get('median_betweenness_rank', 'N/A')}")
            lines.append(f"- **Median degree rank of planted bridges**: {exp_b.get('median_total_degree_rank', 'N/A')}")
        exp_c = gt_results.get("experiment_C_community_recovery", {})
        if exp_c:
            lines.append(f"- **Community ARI**: {exp_c.get('ari', 'N/A')}")
            lines.append(f"- **Community NMI**: {exp_c.get('nmi', 'N/A')}")
        exp_d = gt_results.get("experiment_D_dependency_recovery", {})
        if exp_d.get("dependency_group_results"):
            lines.append(f"- **Planted dependents whose top supplier is the planted critical supplier**: {exp_d.get('top_supplier_identification_rate', 0):.2f}")
            lines.append(f"- **Planted dependents flagged as high-dependency (top {exp_d.get('top_fraction', 0):.0%} of manufacturers)**: {exp_d.get('high_dependency_flag_rate', 0):.2f}")
            n_groups = len(exp_d["dependency_group_results"])
            lines.append(f"- **Critical suppliers in top {exp_d.get('top_fraction', 0):.0%} of suppliers by weighted out-degree**: {exp_d.get('critical_suppliers_in_top_by_out_strength')}/{n_groups}")
            lines.append(f"- **Critical suppliers in top {exp_d.get('top_fraction', 0):.0%} of suppliers by reversed PageRank**: {exp_d.get('critical_suppliers_in_top_by_pagerank_reversed')}/{n_groups}")
        exp_e = gt_results.get("experiment_E_critical_node_resilience", {})
        if exp_e:
            lines.append(f"- **Efficiency change after removing planted hubs**: {exp_e.get('efficiency_change', 'N/A')}")
    lines.append("\n---\n")

    lines.append("## 8. Limitations\n")
    lines += [
        "- Dataset is synthetic and not equivalent to real enterprise supply-chain data",
        "- Synthetic generation rules influence network structure and SNA findings",
        "- SNA identifies structural patterns but does not establish causation",
        "- Centrality does not automatically imply business importance",
        "- Community detection results depend on algorithm choice and graph representation",
        "- Large-graph metrics (path length, efficiency) may use sampling approximations",
        "- Blockchain/decentralized layer is abstracted, not a live implementation",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    main()
