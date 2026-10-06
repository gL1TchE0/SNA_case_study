"""
Supply Chain SNA — Interactive Streamlit Dashboard
PHASE 18: Multi-page interactive analytics dashboard.

Pages:
  1. Overview
  2. Network Explorer
  3. Centrality Analysis
  4. Community Analysis
  5. Dependency Analysis
  6. Temporal Analysis
  7. Resilience Simulation

All displayed data comes from pre-computed experiment results.
No analytical values are hard-coded.

Launch: streamlit run dashboard/app.py
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Page configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain SNA",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Data loading (cached) ─────────────────────────────────────────────────


@st.cache_data
def load_organizations() -> pd.DataFrame:
    """Load organizations from CSV."""
    p = Path("data/synthetic/organizations.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_transactions() -> pd.DataFrame:
    """Load transactions from CSV."""
    p = Path("data/synthetic/transactions.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_resource
def load_graph() -> nx.DiGraph | None:
    """Load the pre-built graph."""
    p = Path("data/processed/supply_chain_graph_frequency.pkl")
    if p.exists():
        with p.open("rb") as fh:
            return pickle.load(fh)
    return None


@st.cache_data
def load_centrality() -> pd.DataFrame:
    """Load centrality results."""
    p = Path("reports/results/centrality.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_community() -> pd.DataFrame:
    """Load community assignments."""
    p = Path("reports/results/communities.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_kcore() -> pd.DataFrame:
    """Load k-core results."""
    p = Path("reports/results/kcore.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_dependencies() -> pd.DataFrame:
    """Load dependency concentration results."""
    p = Path("reports/results/dependencies.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_temporal() -> pd.DataFrame:
    """Load temporal snapshot data."""
    p = Path("reports/results/temporal.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_temporal_centrality() -> pd.DataFrame:
    """Load temporal centrality data."""
    p = Path("reports/results/temporal_centrality.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_json_result(filename: str) -> dict[str, Any]:
    """Load a JSON result file."""
    p = Path(f"reports/results/{filename}")
    if p.exists():
        with p.open() as fh:
            return json.load(fh)
    return {}


@st.cache_data
def load_resilience(strategy: str) -> pd.DataFrame:
    """Load resilience results for a strategy."""
    p = Path(f"reports/results/resilience_{strategy}.csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


def load_ground_truth() -> dict[str, Any]:
    """Load ground-truth metadata."""
    p = Path("data/synthetic/ground_truth.json")
    if p.exists():
        with p.open() as fh:
            return json.load(fh)
    return {}


def check_data_ready() -> bool:
    """Check if the required data files exist."""
    required = [
        Path("data/synthetic/organizations.csv"),
        Path("data/synthetic/transactions.csv"),
        Path("data/processed/supply_chain_graph_frequency.pkl"),
    ]
    return all(p.exists() for p in required)


# ── Sidebar navigation ─────────────────────────────────────────────────────


def sidebar_nav() -> str:
    """Render sidebar navigation and return the selected page."""
    st.sidebar.title("🔗 Supply Chain SNA")
    st.sidebar.markdown("**Social Network Analysis Dashboard**")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigate to",
        [
            "📊 Overview",
            "🌐 Network Explorer",
            "📈 Centrality Analysis",
            "🏘️ Community Analysis",
            "⚠️ Dependency Analysis",
            "⏱️ Temporal Analysis",
            "🛡️ Resilience Simulation",
        ],
    )

    st.sidebar.divider()
    st.sidebar.caption("Data generated with configurable synthetic supply-chain network generator.")
    return page


# ── Page: Overview ─────────────────────────────────────────────────────────


def page_overview() -> None:
    """Render the Overview page."""
    st.title("📊 Supply Chain Network — Overview")
    st.markdown(
        """
        This dashboard presents Social Network Analysis results for a synthetic supply-chain network.
        All metrics are computed from generated transaction data — no values are hard-coded.
        """
    )

    if not check_data_ready():
        st.error("⚠️ Data not ready. Run the full pipeline first.")
        st.code("""python -m generator.generate --config config/default.yaml
python -m graph.build
python -m experiments.run --experiment all
python -m reports.generate""")
        return

    G = load_graph()
    orgs = load_organizations()
    txns = load_transactions()
    net_stats = load_json_result("network_statistics.json")
    comm_stats = load_json_result("community_stats.json")

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Organizations", G.number_of_nodes() if G else len(orgs), help="Total nodes in graph")
    with col2:
        st.metric("Relationships", G.number_of_edges() if G else 0, help="Total directed edges")
    with col3:
        st.metric("Network Density", f"{net_stats.get('density', 0):.5f}", help="Edges / possible edges")
    with col4:
        st.metric("Communities Detected", comm_stats.get("num_communities", "N/A"), help="Louvain community count")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("WCC Count", net_stats.get("weakly_connected_components", "N/A"), help="Weakly connected components")
    with col6:
        st.metric("Largest WCC %", f"{net_stats.get('largest_wcc_fraction', 0)*100:.1f}%")
    with col7:
        months_count = len(txns["month"].unique()) if "month" in txns.columns else 0
        st.metric("Time Periods", months_count, help="Months in dataset")
    with col8:
        st.metric("Total Transactions", len(txns))

    st.divider()

    # Organization type breakdown
    st.subheader("Organization Type Distribution")
    if not orgs.empty and "organization_type" in orgs.columns:
        type_counts = orgs["organization_type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig = px.pie(type_counts, names="Type", values="Count", title="Organizations by Type")
        st.plotly_chart(fig, use_container_width=True)

    # Region breakdown
    if not orgs.empty and "region" in orgs.columns:
        col_a, col_b = st.columns(2)
        with col_a:
            region_counts = orgs["region"].value_counts().reset_index()
            region_counts.columns = ["Region", "Count"]
            fig2 = px.bar(region_counts, x="Region", y="Count", title="Organizations by Region")
            st.plotly_chart(fig2, use_container_width=True)
        with col_b:
            if "month" in txns.columns:
                month_vol = txns.groupby("month")["transaction_value"].sum().reset_index()
                month_vol.columns = ["Month", "Transaction Volume"]
                fig3 = px.line(month_vol, x="Month", y="Transaction Volume", title="Monthly Transaction Volume")
                st.plotly_chart(fig3, use_container_width=True)


# ── Page: Network Explorer ─────────────────────────────────────────────────


def page_network_explorer() -> None:
    """Render the Network Explorer page."""
    st.title("🌐 Network Explorer")
    st.info("Interactive graph view. Large graphs are sampled for performance.")

    G = load_graph()
    centrality_df = load_centrality()
    community_df = load_community()
    orgs = load_organizations()

    if G is None:
        st.error("Graph not found. Run the pipeline first.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        max_nodes = st.slider("Max nodes to display", 50, 500, 200, 50)
    with col2:
        if not orgs.empty and "organization_type" in orgs.columns:
            org_types = ["All"] + sorted(orgs["organization_type"].unique().tolist())
            selected_type = st.selectbox("Organization Type", org_types)
        else:
            selected_type = "All"
    with col3:
        color_by = st.selectbox("Color by", ["organization_type", "region", "community"])

    # Filter graph
    if selected_type != "All" and not orgs.empty:
        filtered_orgs = orgs[orgs["organization_type"] == selected_type]["organization_id"].tolist()
        subG = G.subgraph([n for n in G.nodes() if n in set(filtered_orgs)]).copy()
    else:
        subG = G

    n_total = subG.number_of_nodes()
    st.caption(f"Graph: {n_total} nodes, {subG.number_of_edges()} edges")

    # Render network
    from reports.visualization import plot_network_graph
    fig = plot_network_graph(
        subG,
        node_attr=color_by if color_by != "community" else "organization_type",
        centrality_df=centrality_df if not centrality_df.empty else None,
        community_df=community_df if (color_by == "community" and not community_df.empty) else None,
        max_nodes=max_nodes,
        title=f"Supply-Chain Network ({n_total} nodes filtered)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Node lookup
    st.subheader("Node Details")
    if not centrality_df.empty:
        node_id = st.selectbox("Select a node", centrality_df["node"].tolist()[:100])
        if node_id:
            row = centrality_df[centrality_df["node"] == node_id]
            if not row.empty:
                r = row.iloc[0]
                org_row = orgs[orgs["organization_id"] == node_id] if not orgs.empty else pd.DataFrame()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Organization Info**")
                    if not org_row.empty:
                        for col in ["organization_name", "organization_type", "region", "industry", "size_category", "status"]:
                            if col in org_row.columns:
                                st.write(f"- **{col.replace('_',' ').title()}**: {org_row.iloc[0][col]}")
                with col_b:
                    st.write("**Centrality Metrics**")
                    for metric in ["in_degree", "out_degree", "total_degree", "betweenness", "closeness", "eigenvector", "pagerank", "pagerank_reversed"]:
                        if metric in r.index:
                            st.write(f"- **{metric.replace('_',' ').title()}**: {r[metric]:.6f}")


# ── Page: Centrality Analysis ─────────────────────────────────────────────


def page_centrality() -> None:
    """Render the Centrality Analysis page."""
    st.title("📈 Centrality Analysis")
    st.markdown("Comparing five centrality measures across the supply-chain network.")

    centrality_df = load_centrality()
    if centrality_df.empty:
        st.warning("Centrality results not found. Run experiments first.")
        return

    top_n = st.slider("Top N organizations", 5, 50, 20)

    # Tabs for each metric
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Degree", "Betweenness", "PageRank", "Closeness", "Comparison"]
    )

    with tab1:
        st.subheader("Top Organizations by Total Degree")
        st.markdown("> **High in-degree**: many suppliers. **High out-degree**: supplies many organizations.")
        top = centrality_df.nlargest(top_n, "total_degree")[["node", "in_degree", "out_degree", "total_degree"]]
        fig = px.bar(top, x="node", y="total_degree", color="in_degree", title="Top by Total Degree")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top, use_container_width=True)

    with tab2:
        st.subheader("Top Organizations by Betweenness Centrality")
        st.markdown("> **High betweenness**: lies on many shortest paths — a bridge or bottleneck.")
        if "betweenness" in centrality_df.columns:
            top = centrality_df.nlargest(top_n, "betweenness")[["node", "betweenness"]]
            fig = px.bar(top, x="node", y="betweenness", title="Top by Betweenness", color="betweenness", color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top, use_container_width=True)

    with tab3:
        st.subheader("Top Organizations by PageRank")
        st.markdown("> **High PageRank**: important because it receives links from important nodes.")
        if "pagerank" in centrality_df.columns:
            top = centrality_df.nlargest(top_n, "pagerank")[["node", "pagerank"]]
            fig = px.bar(top, x="node", y="pagerank", title="Top by PageRank", color="pagerank", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top, use_container_width=True)

    with tab4:
        st.subheader("Top Organizations by Closeness Centrality")
        st.markdown("> **High closeness**: structurally close to all other organizations.")
        if "closeness" in centrality_df.columns:
            top = centrality_df.nlargest(top_n, "closeness")[["node", "closeness"]]
            fig = px.bar(top, x="node", y="closeness", title="Top by Closeness")
            st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("Rank Correlations Between Metrics")
        cent_stats = load_json_result("centrality_stats.json")
        if cent_stats.get("rank_correlations"):
            corr_data = [
                {"Metric Pair": k, "Spearman r": v.get("spearman_r", 0)}
                for k, v in cent_stats["rank_correlations"].items()
                if isinstance(v, dict)
            ]
            corr_df = pd.DataFrame(corr_data)
            fig = px.bar(corr_df, x="Metric Pair", y="Spearman r", title="Rank Correlations",
                        color="Spearman r", color_continuous_scale="RdBu", range_color=[-1, 1])
            st.plotly_chart(fig, use_container_width=True)

        # Multi-metric scatter
        st.subheader("Degree vs Betweenness (All Nodes)")
        if "betweenness" in centrality_df.columns and "total_degree" in centrality_df.columns:
            fig2 = px.scatter(
                centrality_df.head(1000),
                x="total_degree", y="betweenness",
                hover_name="node",
                title="Degree vs Betweenness",
                labels={"total_degree": "Total Degree", "betweenness": "Betweenness Centrality"},
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Degree distribution
    st.subheader("Degree Distribution")
    from reports.visualization import plot_degree_distribution
    fig = plot_degree_distribution(centrality_df, output_dir=Path("reports/figures"))
    st.plotly_chart(fig, use_container_width=True)


# ── Page: Community Analysis ─────────────────────────────────────────────


def page_communities() -> None:
    """Render the Community Analysis page."""
    st.title("🏘️ Community Analysis")

    community_df = load_community()
    comm_stats = load_json_result("community_stats.json")
    gt_results = load_json_result("ground_truth_results.json")

    if community_df.empty:
        st.warning("Community results not found. Run experiments first.")
        return

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Communities Detected", comm_stats.get("num_communities", "N/A"))
    with col2:
        mod = comm_stats.get("modularity")
        st.metric("Modularity", f"{mod:.4f}" if mod else "N/A",
                  help="Higher modularity = more distinct communities")
    with col3:
        frac = comm_stats.get("inter_community_fraction", 0)
        st.metric("Inter-community Edge Fraction", f"{frac:.4f}")

    # Community sizes
    st.subheader("Community Size Distribution")
    from reports.visualization import plot_community_sizes
    fig = plot_community_sizes(community_df, output_dir=Path("reports/figures"))
    st.plotly_chart(fig, use_container_width=True)

    # Community membership table
    st.subheader("Community Members")
    selected_community = st.selectbox("Select Community", sorted(community_df["community_id"].unique()))
    members = community_df[community_df["community_id"] == selected_community]
    st.write(f"Members: {len(members)}")
    st.dataframe(members, use_container_width=True)

    # Ground-truth evaluation
    if gt_results.get("experiment_C_community_recovery"):
        st.subheader("Community Recovery Evaluation")
        comm_eval = gt_results["experiment_C_community_recovery"]
        ari = comm_eval.get("ari")
        nmi = comm_eval.get("nmi")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Adjusted Rand Index (ARI)", f"{ari:.4f}" if ari is not None else "N/A",
                      help="1.0 = perfect recovery, 0.0 = random")
        with col_b:
            st.metric("Normalized Mutual Information (NMI)", f"{nmi:.4f}" if nmi is not None else "N/A")
        if comm_eval.get("interpretation"):
            st.info(comm_eval["interpretation"])


# ── Page: Dependency Analysis ─────────────────────────────────────────────


def page_dependencies() -> None:
    """Render the Dependency Analysis page."""
    st.title("⚠️ Dependency Analysis")
    st.markdown(
        """
        Structural dependency analysis identifies organizations with concentrated upstream supply.
        
        **Metrics used:**
        - *Supplier dependency ratio* = quantity_from_top_supplier / total_quantity
        - *Single-source nodes* = organizations with only one upstream supplier
        - *Critical upstream nodes* = organizations that many others depend on (top 10% out-degree)
        
        > Note: These are structural metrics. High dependency concentration is not automatically 
        > a business risk without additional context.
        """
    )

    dep_df = load_dependencies()
    dep_summary = load_json_result("dependency_summary.json")
    centrality_df = load_centrality()
    gt_results = load_json_result("ground_truth_results.json")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Single-Source Nodes", dep_summary.get("single_source_count", "N/A"),
                  help="Nodes with exactly one upstream supplier")
    with col2:
        st.metric("High Concentration (>80%)", dep_summary.get("high_concentration_count", "N/A"),
                  help="Nodes where >80% of supply from one source")
    with col3:
        st.metric("Critical Upstream Nodes", len(dep_summary.get("critical_upstream_nodes", [])))

    if not dep_df.empty:
        st.subheader("Upstream Concentration Distribution")
        if "supplier_dependency_ratio" in dep_df.columns:
            fig = px.histogram(dep_df, x="supplier_dependency_ratio", nbins=20,
                              title="Distribution of Supplier Dependency Ratios",
                              labels={"supplier_dependency_ratio": "Dependency Ratio (0=diversified, 1=single-source)"})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top Concentrated Dependencies")
        display_cols = [c for c in ["node", "node_type", "num_suppliers", "top_supplier", "supplier_dependency_ratio"] if c in dep_df.columns]
        st.dataframe(dep_df[display_cols].head(50), use_container_width=True)

    # Bridge nodes (from betweenness)
    if not centrality_df.empty and "betweenness" in centrality_df.columns:
        st.subheader("High-Betweenness Bridge Organizations")
        bridges = centrality_df.nlargest(20, "betweenness")[["node", "betweenness", "in_degree", "out_degree"]]
        st.dataframe(bridges, use_container_width=True)

    # Dependency group evaluation
    if gt_results.get("experiment_D_dependency_recovery"):
        st.subheader("Ground-Truth Dependency Group Evaluation")
        dep_eval = gt_results["experiment_D_dependency_recovery"]
        st.write(
            f"Planted dependents whose top supplier is the planted critical supplier: "
            f"{dep_eval.get('top_supplier_identification_rate', 0):.0%}; flagged as high-dependency: "
            f"{dep_eval.get('high_dependency_flag_rate', 0):.0%}"
        )
        if dep_eval.get("dependency_group_results"):
            dep_group_df = pd.DataFrame(dep_eval["dependency_group_results"])
            st.dataframe(dep_group_df, use_container_width=True)


# ── Page: Temporal Analysis ────────────────────────────────────────────────


def page_temporal() -> None:
    """Render the Temporal Analysis page."""
    st.title("⏱️ Temporal Analysis")
    st.markdown("How does the supply-chain network evolve over time?")

    snapshot_df = load_temporal()
    node_time_df = load_temporal_centrality()

    if snapshot_df.empty:
        st.warning("Temporal results not found. Run: python -m experiments.run --experiment temporal")
        return

    # Date range selector
    months = sorted(snapshot_df["month"].unique().tolist())
    col1, col2 = st.columns(2)
    with col1:
        start_idx = st.selectbox("Start Month", range(len(months)), format_func=lambda i: months[i])
    with col2:
        end_idx = st.selectbox("End Month", range(len(months)), index=len(months)-1, format_func=lambda i: months[i])

    filtered = snapshot_df.iloc[start_idx:end_idx+1]

    # Network evolution
    from reports.visualization import plot_temporal_metrics
    fig = plot_temporal_metrics(filtered)
    st.plotly_chart(fig, use_container_width=True)

    # Per-node centrality over time
    if not node_time_df.empty:
        st.subheader("Node Centrality Evolution")
        available_nodes = sorted(node_time_df["node"].unique().tolist())
        selected_nodes = st.multiselect("Select nodes to track", available_nodes, default=available_nodes[:3])

        if selected_nodes:
            metric = st.selectbox("Centrality metric", ["betweenness", "pagerank", "total_degree"])
            node_filtered = node_time_df[node_time_df["node"].isin(selected_nodes)]
            fig2 = px.line(node_filtered, x="month", y=metric, color="node",
                          title=f"{metric.title()} Evolution for Selected Nodes",
                          markers=True)
            st.plotly_chart(fig2, use_container_width=True)

    # Raw snapshot table
    with st.expander("Snapshot Data Table"):
        st.dataframe(filtered, use_container_width=True)


# ── Page: Resilience Simulation ────────────────────────────────────────────


def page_resilience() -> None:
    """Render the Resilience Simulation page."""
    st.title("🛡️ Resilience Simulation")
    st.markdown(
        """
        Node removal experiments comparing four attack strategies.
        **Random removal** uses multiple seeds; mean ± std shown.
        """
    )

    strategies = ["random", "degree", "betweenness", "pagerank"]
    loaded = {s: load_resilience(s) for s in strategies}
    available = {s: df for s, df in loaded.items() if not df.empty}

    if not available:
        st.warning("Resilience results not found. Run: python -m experiments.run --experiment resilience")
        return

    selected_strategies = st.multiselect(
        "Attack strategies to compare",
        list(available.keys()),
        default=list(available.keys()),
    )

    # Degradation curves
    st.subheader("Network Degradation Curves")
    from reports.visualization import plot_resilience_curves
    fig = plot_resilience_curves(
        {s: available[s] for s in selected_strategies if s in available}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Stats at specific removal fractions
    st.subheader("Metrics at Specific Removal Fractions")
    target_frac = st.select_slider("View at fraction removed",
                                    options=[0.0, 0.05, 0.10, 0.15, 0.20, 0.30],
                                    value=0.10)

    rows = []
    for strategy in selected_strategies:
        df = available.get(strategy, pd.DataFrame())
        if df.empty:
            continue
        col_lcc = "lcc_mean" if "lcc_mean" in df.columns else "largest_component_fraction"
        col_eff = "efficiency_mean" if "efficiency_mean" in df.columns else "network_efficiency"
        closest = df.iloc[(df["fraction_removed"] - target_frac).abs().argsort()[:1]]
        if not closest.empty:
            r = closest.iloc[0]
            rows.append({
                "Strategy": strategy,
                "Fraction Removed": f"{r['fraction_removed']:.2f}",
                "LCC Fraction": f"{r.get(col_lcc, 0):.4f}",
                "Network Efficiency": f"{r.get(col_eff, 0):.4f}",
            })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # Critical node resilience from ground truth
    gt_results = load_json_result("ground_truth_results.json")
    if gt_results.get("experiment_E_critical_node_resilience"):
        st.subheader("Critical Node Removal (Ground-Truth Experiment)")
        exp_e = gt_results["experiment_E_critical_node_resilience"]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Nodes Removed", exp_e.get("nodes_removed", "N/A"))
        with col_b:
            st.metric("Efficiency Change", f"{exp_e.get('efficiency_change', 0):.4f}")
        with col_c:
            st.metric("LCC Change", exp_e.get("lcc_change", "N/A"))


# ── Main routing ─────────────────────────────────────────────────────────


def main() -> None:
    """Main dashboard entry point."""
    page = sidebar_nav()

    if page == "📊 Overview":
        page_overview()
    elif page == "🌐 Network Explorer":
        page_network_explorer()
    elif page == "📈 Centrality Analysis":
        page_centrality()
    elif page == "🏘️ Community Analysis":
        page_communities()
    elif page == "⚠️ Dependency Analysis":
        page_dependencies()
    elif page == "⏱️ Temporal Analysis":
        page_temporal()
    elif page == "🛡️ Resilience Simulation":
        page_resilience()


if __name__ == "__main__":
    main()
