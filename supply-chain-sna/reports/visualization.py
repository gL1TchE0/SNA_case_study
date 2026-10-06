"""
Supply Chain SNA — Visualization Engine
PHASE 17: Generates reusable plots for all SNA analyses.

All plots use actual computed data — no hard-coded values.
Saves PNG to the reports/figures directory, plus a README.md with a
caption for every figure.
"""
from __future__ import annotations

import logging
import math
import random
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

# ── Shared style ──────────────────────────────────────────────────────────────
# Categorical hues are assigned in this fixed order and never cycled; anything
# past the last slot is folded into "Other".
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
OTHER_COLOR = "#b5b3ac"
NEUTRAL = "#898781"
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e9e8e4"
SEQUENTIAL_HUE = "#2a78d6"
DIVERGING = [[0.0, "#eb6834"], [0.5, "#f0efec"], [1.0, "#2a78d6"]]

ORG_TYPE_ORDER = ["supplier", "manufacturer", "distributor", "warehouse", "logistics_provider", "retailer"]
ORG_TYPE_PREFIX = {"SUP": "supplier", "MFG": "manufacturer", "DST": "distributor",
                   "WHS": "warehouse", "LOG": "logistics_provider", "RET": "retailer"}
ORG_TYPE_COLOR = dict(zip(ORG_TYPE_ORDER, CATEGORICAL))

METRIC_LABELS = {
    "in_degree": "In-degree",
    "out_degree": "Out-degree",
    "total_degree": "Total degree",
    "betweenness": "Betweenness",
    "closeness": "Closeness",
    "eigenvector": "Eigenvector",
    "pagerank": "PageRank",
    "pagerank_reversed": "PageRank (reversed)",
}

STRATEGY_STYLE = {
    "random": ("Random failure", NEUTRAL),
    "degree": ("Degree attack", CATEGORICAL[0]),
    "betweenness": ("Betweenness attack", CATEGORICAL[1]),
    "pagerank": ("PageRank attack", CATEGORICAL[2]),
}

CAPTIONS: dict[str, str] = {
    "network_graph": (
        "Supply-chain network. Each dot is an organization, coloured by organization type and "
        "sized by total degree. Organizations are placed in one cluster per region, so lines "
        "inside a cluster are intra-region relationships and lines between clusters are "
        "inter-region relationships."
    ),
    "network_graph_community": (
        "The same network coloured and clustered by the communities Louvain detected "
        "(on the undirected projection). Dense clusters with few lines between them indicate "
        "well-separated communities."
    ),
    "degree_distribution": (
        "Degree distribution. Top row: histograms of in-degree, out-degree and total degree. "
        "Bottom row: the share of organizations with degree at least k on log-log axes; a long "
        "right tail means a few organizations are far better connected than the rest."
    ),
    "centrality_comparison": (
        "Top 15 organizations under each centrality measure, coloured by organization type. "
        "Different measures promote different kinds of organization, which is why no single "
        "measure is treated as 'importance'."
    ),
    "centrality_heatmap": (
        "Spearman rank correlation between every pair of centrality measures. Values near 1 mean "
        "two measures rank organizations the same way; values near 0 or below mean they capture "
        "different structural roles."
    ),
    "community_sizes": (
        "Size of each detected community, split by the planted region of its members. A bar in a "
        "single colour is a detected community that matches one planted region."
    ),
    "kcore_distribution": (
        "K-core decomposition (undirected projection): number of organizations at each core "
        "number, split by organization type. Higher core numbers are the densely interconnected "
        "centre of the network; low numbers are the periphery."
    ),
    "bridge_hub_scatter": (
        "Total degree against betweenness for every organization, with the planted hubs and "
        "planted bridges highlighted. Bridges sit high on betweenness relative to their degree; "
        "hubs sit far right on degree."
    ),
    "dependency_concentration": (
        "Supplier dependency ratio of every manufacturer: the share of its inbound transaction "
        "volume that comes from its single largest supplier (logistics edges excluded). The "
        "manufacturers planted as dependent on a critical supplier are marked."
    ),
    "temporal_metrics": (
        "Monthly evolution of the network. Each panel is one measure computed on that month's "
        "snapshot (organizations and relationships active in that month)."
    ),
    "resilience_curves": (
        "Network degradation as organizations are removed, under random failure and three "
        "targeted attacks. Left: share of remaining organizations in the largest connected "
        "component. Right: global efficiency. Random failure is the mean over several seeds."
    ),
}


def _style(fig: go.Figure, title: str, height: int, width: int = 1000, showlegend: bool = True) -> go.Figure:
    """Apply the shared chart style."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=INK), x=0.01, xanchor="left"),
        font=dict(family="Inter, Helvetica, Arial, sans-serif", size=12, color=INK_SECONDARY),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        height=height,
        width=width,
        showlegend=showlegend,
        legend=dict(font=dict(color=INK_SECONDARY), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=30, t=80, b=60),
        bargap=0.15,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(color=NEUTRAL))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(color=NEUTRAL))
    fig.update_annotations(font=dict(size=13, color=INK))
    return fig


def _label(value: Any) -> str:
    return str(value).replace("_", " ").capitalize()


def _org_type_of(node: str) -> str:
    return ORG_TYPE_PREFIX.get(str(node).split("-")[0], "unknown")


def save_figure(fig: go.Figure, path: Path, formats: list[str] | None = None) -> None:
    """Save a Plotly figure in one or more formats.

    Args:
        fig: Plotly figure.
        path: Output path (without extension).
        formats: List of formats. Defaults to ["png"].
    """
    if formats is None:
        formats = ["png"]
    for fmt in formats:
        out_path = path.with_suffix(f".{fmt}")
        try:
            if fmt == "html":
                fig.write_html(str(out_path))
            else:
                fig.write_image(str(out_path), scale=2)
            logger.info("Saved figure → %s", out_path)
        except Exception as exc:
            logger.warning("Could not save %s: %s", out_path, exc)


def plot_degree_distribution(
    centrality_df: pd.DataFrame,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot degree histograms and log-log complementary cumulative distributions.

    Args:
        centrality_df: Centrality DataFrame with degree columns.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    cols = [c for c in ["in_degree", "out_degree", "total_degree"] if c in centrality_df.columns]
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[METRIC_LABELS[c] for c in cols] + [f"{METRIC_LABELS[c]}: share with degree ≥ k" for c in cols],
        vertical_spacing=0.18,
    )

    for i, col in enumerate(cols, 1):
        values = centrality_df[col]
        fig.add_trace(
            go.Histogram(x=values, nbinsx=30, marker=dict(color=SEQUENTIAL_HUE, line=dict(color=SURFACE, width=1)),
                         hovertemplate="degree %{x}<br>%{y} organizations<extra></extra>"),
            row=1, col=i,
        )
        positive = np.sort(values[values > 0].to_numpy())
        if len(positive):
            ks = np.unique(positive)
            ccdf = [(positive >= k).mean() for k in ks]
            fig.add_trace(
                go.Scatter(x=ks, y=ccdf, mode="markers", marker=dict(color=SEQUENTIAL_HUE, size=6),
                           hovertemplate="k = %{x}<br>share ≥ k: %{y:.3f}<extra></extra>"),
                row=2, col=i,
            )
        fig.update_xaxes(title_text="Degree", row=1, col=i)
        fig.update_xaxes(title_text="Degree k (log)", type="log", row=2, col=i)
        fig.update_yaxes(type="log", row=2, col=i)
    fig.update_yaxes(title_text="Organizations", row=1, col=1)
    fig.update_yaxes(title_text="Share of organizations (log)", row=2, col=1)

    _style(fig, "Degree distribution of the supply-chain network", height=700, showlegend=False)
    if output_dir:
        save_figure(fig, output_dir / "degree_distribution", ["png"])
    return fig


def plot_centrality_comparison(
    centrality_df: pd.DataFrame,
    top_n: int = 15,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot top-N nodes by each centrality metric, coloured by organization type.

    Args:
        centrality_df: Combined centrality DataFrame.
        top_n: Number of top nodes to show.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    metrics = ["total_degree", "betweenness", "closeness", "eigenvector", "pagerank", "pagerank_reversed"]
    available = [m for m in metrics if m in centrality_df.columns]
    if not available:
        return go.Figure()

    n_cols = 3
    n_rows = math.ceil(len(available) / n_cols)
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[METRIC_LABELS[m] for m in available],
        horizontal_spacing=0.14, vertical_spacing=0.1,
    )

    shown_types: set[str] = set()
    for idx, metric in enumerate(available):
        row, col = idx // n_cols + 1, idx % n_cols + 1
        top = centrality_df.nlargest(top_n, metric).iloc[::-1]
        types = [_org_type_of(n) for n in top["node"]]
        for otype in ORG_TYPE_ORDER:
            mask = [t == otype for t in types]
            if not any(mask):
                continue
            sub = top[mask]
            fig.add_trace(
                go.Bar(
                    y=sub["node"], x=sub[metric], orientation="h",
                    name=_label(otype), legendgroup=otype,
                    showlegend=otype not in shown_types,
                    marker=dict(color=ORG_TYPE_COLOR[otype]),
                    hovertemplate="%{y}<br>" + METRIC_LABELS[metric] + ": %{x:.4g}<extra></extra>",
                ),
                row=row, col=col,
            )
            shown_types.add(otype)
        fig.update_yaxes(categoryorder="array", categoryarray=top["node"].tolist(),
                         tickfont=dict(size=9), row=row, col=col)

    _style(fig, f"Top {top_n} organizations by centrality measure", height=420 * n_rows, width=1200)
    fig.update_layout(barmode="overlay", legend=dict(orientation="h", y=-0.05, title_text="Organization type"))
    if output_dir:
        save_figure(fig, output_dir / "centrality_comparison", ["png"])
    return fig


def plot_centrality_heatmap(
    centrality_df: pd.DataFrame,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot the Spearman rank-correlation matrix between centrality measures.

    Args:
        centrality_df: Combined centrality DataFrame.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    metrics = [m for m in METRIC_LABELS if m in centrality_df.columns]
    if len(metrics) < 2:
        return go.Figure()

    corr = centrality_df[metrics].corr(method="spearman")
    labels = [METRIC_LABELS[m] for m in metrics]
    fig = go.Figure(
        go.Heatmap(
            z=corr.values, x=labels, y=labels,
            zmin=-1, zmax=1, colorscale=DIVERGING,
            xgap=2, ygap=2,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}", textfont=dict(color=INK, size=12),
            colorbar=dict(title="Spearman ρ"),
            hovertemplate="%{y} vs %{x}<br>ρ = %{z:.3f}<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    _style(fig, "Rank correlation between centrality measures", height=650, width=850, showlegend=False)
    fig.update_layout(margin=dict(l=150, b=130))
    if output_dir:
        save_figure(fig, output_dir / "centrality_heatmap", ["png"])
    return fig


def _grouped_layout(G: nx.Graph, groups: dict[Any, list[str]], seed: int = 42) -> dict[str, tuple[float, float]]:
    """Lay out nodes in one cluster per group, clusters arranged on a circle.

    Args:
        G: Graph to lay out.
        groups: Mapping group label → node list (largest first).
        seed: Layout seed.

    Returns:
        Mapping node → (x, y).
    """
    pos: dict[str, tuple[float, float]] = {}
    n_groups = max(1, len(groups))
    total = max(1, sum(len(v) for v in groups.values()))
    ring = 1.0 if n_groups > 1 else 0.0
    for i, (_, nodes) in enumerate(groups.items()):
        angle = 2 * math.pi * i / n_groups
        cx, cy = ring * math.cos(angle), ring * math.sin(angle)
        radius = 0.9 * math.sin(math.pi / max(2, n_groups)) * math.sqrt(len(nodes) / (total / n_groups))
        radius = min(radius, 0.45) if n_groups > 1 else 1.0
        sub = G.subgraph(nodes)
        try:
            local = nx.spring_layout(sub, seed=seed, k=2.0 / max(1.0, math.sqrt(len(nodes))), iterations=60)
        except Exception:
            local = nx.random_layout(sub, seed=seed)
        # Scale by the typical spread, not the extreme one, so a few loosely
        # attached nodes cannot squeeze the rest of the cluster into a point.
        pts = np.array([local[n] for n in sub.nodes()], dtype=float).reshape(-1, 2)
        pts = pts - np.median(pts, axis=0)
        dist = np.hypot(pts[:, 0], pts[:, 1])
        spread = float(np.percentile(dist, 90)) if len(dist) > 1 else 1.0
        pts = pts / (spread or 1.0)
        dist = np.hypot(pts[:, 0], pts[:, 1])
        over = dist > 1.25
        pts[over] = pts[over] / dist[over, None] * 1.25
        for node, (x, y) in zip(sub.nodes(), pts):
            pos[node] = (cx + radius * float(x), cy + radius * float(y))
    return pos


def plot_network_graph(
    G: nx.DiGraph,
    node_attr: str = "organization_type",
    centrality_df: pd.DataFrame | None = None,
    community_df: pd.DataFrame | None = None,
    max_nodes: int = 1500,
    output_dir: Path | None = None,
    title: str | None = None,
    group_attr: str = "region",
    filename: str | None = None,
) -> go.Figure:
    """Plot the network with categorical node colours and a clustered layout.

    If ``community_df`` is given, nodes are coloured and clustered by detected
    community. Otherwise they are coloured by ``node_attr`` and clustered by
    ``group_attr``.

    Args:
        G: Directed graph.
        node_attr: Node attribute to use for colouring.
        centrality_df: Optional centrality DataFrame for node sizing.
        community_df: Optional community DataFrame for colouring.
        max_nodes: Maximum nodes to render (samples if larger).
        output_dir: Directory to save figure.
        title: Figure title.
        group_attr: Node attribute used to cluster the layout.
        filename: Output file name without extension.

    Returns:
        Plotly figure.
    """
    by_community = community_df is not None and not community_df.empty
    if filename is None:
        filename = "network_graph_community" if by_community else "network_graph"

    nodes = list(G.nodes())
    if len(nodes) > max_nodes:
        nodes = random.Random(42).sample(nodes, max_nodes)
        logger.info("Sampled %d/%d nodes for visualization", max_nodes, G.number_of_nodes())
    subG = G.subgraph(nodes)
    U = subG.to_undirected()

    # ── Categories (colour) and groups (layout) ───────────────────────────────
    if by_community:
        comm_map = dict(zip(community_df["node"], community_df["community_id"]))
        category = {n: comm_map.get(n, -1) for n in subG.nodes()}
        sizes = pd.Series(category).value_counts()
        ordered = sizes.index.tolist()
        names = {c: f"Community {c} ({sizes[c]})" for c in ordered}
        group = dict(category)
        legend_title = "Detected community"
    else:
        category = {n: subG.nodes[n].get(node_attr, "unknown") for n in subG.nodes()}
        present = set(category.values())
        ordered = [t for t in ORG_TYPE_ORDER if t in present] if node_attr == "organization_type" else []
        ordered += sorted(present - set(ordered), key=str)
        names = {c: _label(c) for c in ordered}
        group = {n: subG.nodes[n].get(group_attr, "unknown") for n in subG.nodes()}
        legend_title = _label(node_attr)

    colors = {c: (CATEGORICAL[i] if i < len(CATEGORICAL) - 1 or len(ordered) <= len(CATEGORICAL) else OTHER_COLOR)
              for i, c in enumerate(ordered)}
    folded = [c for i, c in enumerate(ordered) if colors[c] == OTHER_COLOR]

    groups: dict[Any, list[str]] = {}
    for n, g in group.items():
        groups.setdefault(g, []).append(n)
    groups = dict(sorted(groups.items(), key=lambda kv: (-len(kv[1]), str(kv[0]))))
    pos = _grouped_layout(U, groups)

    # ── Edges: within a cluster vs. between clusters ──────────────────────────
    intra_x: list[float | None] = []
    intra_y: list[float | None] = []
    inter_x: list[float | None] = []
    inter_y: list[float | None] = []
    for u, v in subG.edges():
        xs, ys = (intra_x, intra_y) if group[u] == group[v] else (inter_x, inter_y)
        xs += [pos[u][0], pos[v][0], None]
        ys += [pos[u][1], pos[v][1], None]

    traces: list[go.Scatter] = [
        go.Scatter(x=inter_x, y=inter_y, mode="lines", line=dict(width=0.4, color="rgba(137,135,129,0.18)"),
                   hoverinfo="none", showlegend=False),
        go.Scatter(x=intra_x, y=intra_y, mode="lines", line=dict(width=0.4, color="rgba(137,135,129,0.30)"),
                   hoverinfo="none", showlegend=False),
    ]

    # ── Nodes: one trace per category so the legend is categorical ────────────
    if centrality_df is not None and "total_degree" in centrality_df.columns:
        deg_map = dict(zip(centrality_df["node"], centrality_df["total_degree"]))
    else:
        deg_map = dict(subG.degree())
    max_deg = max(1, max((deg_map.get(n, 0) for n in subG.nodes()), default=1))

    def _add_nodes(members: list[str], name: str, color: str) -> None:
        traces.append(
            go.Scatter(
                x=[pos[n][0] for n in members], y=[pos[n][1] for n in members],
                mode="markers", name=name,
                marker=dict(
                    size=[6 + 20 * math.sqrt(deg_map.get(n, 0) / max_deg) for n in members],
                    color=color, line=dict(color=SURFACE, width=1), opacity=0.95,
                ),
                text=[
                    f"{n}<br>Type: {_label(subG.nodes[n].get('organization_type', ''))}"
                    f"<br>Region: {subG.nodes[n].get('region', '')}"
                    f"<br>Total degree: {deg_map.get(n, 0)}"
                    for n in members
                ],
                hoverinfo="text",
            )
        )

    for c in ordered:
        if c in folded:
            continue
        _add_nodes([n for n in subG.nodes() if category[n] == c], names[c], colors[c])
    if folded:
        others = [n for n in subG.nodes() if category[n] in folded]
        _add_nodes(others, f"Other ({len(folded)} smaller, {len(others)})", OTHER_COLOR)

    fig = go.Figure(data=traces)

    # Cluster labels
    if len(groups) > 1:
        for i, (g, members) in enumerate(groups.items()):
            angle = 2 * math.pi * i / len(groups)
            label = f"Community {g}" if by_community else str(g)
            fig.add_annotation(
                x=1.75 * math.cos(angle), y=1.75 * math.sin(angle),
                text=f"<b>{label}</b><br>{len(members)} orgs",
                showarrow=False, font=dict(size=11, color=INK_SECONDARY),
            )

    if title is None:
        title = (
            "Supply-chain network by detected community" if by_community
            else f"Supply-chain network by {_label(node_attr).lower()}, clustered by {group_attr}"
        )
    _style(fig, title, height=900, width=1100)
    fig.update_layout(
        hovermode="closest",
        legend=dict(title_text=legend_title, itemsizing="constant"),
        xaxis=dict(visible=False, range=[-2.05, 2.05]),
        yaxis=dict(visible=False, range=[-2.05, 2.05], scaleanchor="x"),
        margin=dict(l=20, r=20, t=70, b=20),
    )

    if output_dir:
        save_figure(fig, output_dir / filename, ["png"])
    return fig


def plot_community_sizes(
    community_df: pd.DataFrame,
    output_dir: Path | None = None,
    G: nx.DiGraph | None = None,
) -> go.Figure:
    """Plot detected community sizes, split by planted region when available.

    Args:
        community_df: Community assignment DataFrame.
        output_dir: Directory to save figure.
        G: Optional graph whose node 'region' attribute gives the planted community.

    Returns:
        Plotly figure.
    """
    if community_df.empty:
        return go.Figure()

    df = community_df.copy()
    order = df["community_id"].value_counts().index.tolist()
    x_labels = [f"C{c}" for c in order]
    fig = go.Figure()

    if G is not None:
        df["region"] = [G.nodes[n].get("region", "unknown") if n in G else "unknown" for n in df["node"]]
        table = df.groupby(["community_id", "region"]).size().unstack(fill_value=0).reindex(order)
        for i, region in enumerate(sorted(table.columns)):
            fig.add_trace(
                go.Bar(
                    x=x_labels, y=table[region], name=str(region),
                    marker=dict(color=CATEGORICAL[i] if i < len(CATEGORICAL) else OTHER_COLOR,
                                line=dict(color=SURFACE, width=2)),
                    hovertemplate="%{x}<br>" + str(region) + ": %{y} organizations<extra></extra>",
                )
            )
        fig.update_layout(barmode="stack")
        title = "Detected communities and the planted regions of their members"
    else:
        sizes = df["community_id"].value_counts().reindex(order)
        fig.add_trace(go.Bar(x=x_labels, y=sizes, marker=dict(color=SEQUENTIAL_HUE),
                             hovertemplate="%{x}<br>%{y} organizations<extra></extra>"))
        title = "Community size distribution"

    _style(fig, title, height=500, showlegend=G is not None)
    fig.update_layout(legend=dict(title_text="Planted region"))
    fig.update_xaxes(title_text="Detected community (largest first)", type="category")
    fig.update_yaxes(title_text="Number of organizations")
    if output_dir:
        save_figure(fig, output_dir / "community_sizes", ["png"])
    return fig


def plot_kcore_distribution(
    kcore_df: pd.DataFrame,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot number of organizations per core number, split by organization type.

    Args:
        kcore_df: K-core DataFrame with columns node, core_number.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    if kcore_df.empty:
        return go.Figure()

    df = kcore_df.copy()
    df["org_type"] = df["node"].map(_org_type_of)
    table = df.groupby(["core_number", "org_type"]).size().unstack(fill_value=0).sort_index()

    fig = go.Figure()
    for otype in ORG_TYPE_ORDER:
        if otype not in table.columns:
            continue
        fig.add_trace(
            go.Bar(
                x=table.index, y=table[otype], name=_label(otype),
                marker=dict(color=ORG_TYPE_COLOR[otype], line=dict(color=SURFACE, width=2)),
                hovertemplate="core %{x}<br>" + _label(otype) + ": %{y}<extra></extra>",
            )
        )
    _style(fig, "K-core decomposition by organization type", height=500)
    fig.update_layout(barmode="stack", legend=dict(title_text="Organization type"))
    fig.update_xaxes(title_text="Core number (k)", dtick=1)
    fig.update_yaxes(title_text="Number of organizations")
    if output_dir:
        save_figure(fig, output_dir / "kcore_distribution", ["png"])
    return fig


def plot_bridge_hub_scatter(
    centrality_df: pd.DataFrame,
    ground_truth: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot total degree vs. betweenness, highlighting planted hubs and bridges.

    Args:
        centrality_df: Combined centrality DataFrame.
        ground_truth: Ground-truth dictionary (planted_hubs, planted_bridges).
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    if centrality_df.empty or "betweenness" not in centrality_df.columns:
        return go.Figure()

    ground_truth = ground_truth or {}
    hubs = set(ground_truth.get("planted_hubs", []))
    bridges = set(ground_truth.get("planted_bridges", []))
    df = centrality_df
    rest = df[~df["node"].isin(hubs | bridges)]

    hover = "%{text}<br>Total degree: %{x}<br>Betweenness: %{y:.4f}<extra></extra>"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rest["total_degree"], y=rest["betweenness"], mode="markers", name="Other organizations",
        text=rest["node"], hovertemplate=hover,
        marker=dict(color=OTHER_COLOR, size=6, opacity=0.6),
    ))
    for name, members, color, symbol in [
        ("Planted hub", hubs, CATEGORICAL[0], "circle"),
        ("Planted bridge", bridges, CATEGORICAL[1], "diamond"),
    ]:
        sub = df[df["node"].isin(members)]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["total_degree"], y=sub["betweenness"], mode="markers", name=name,
            text=sub["node"], hovertemplate=hover,
            marker=dict(color=color, size=12, symbol=symbol, line=dict(color=SURFACE, width=2)),
        ))

    _style(fig, "Hubs and bridges: degree against betweenness", height=600)
    fig.update_xaxes(title_text="Total degree")
    fig.update_yaxes(title_text="Betweenness centrality (normalized)")
    if output_dir:
        save_figure(fig, output_dir / "bridge_hub_scatter", ["png"])
    return fig


def plot_dependency_concentration(
    dep_df: pd.DataFrame,
    ground_truth: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot manufacturers' supplier dependency ratios, marking planted dependents.

    Args:
        dep_df: Upstream concentration DataFrame.
        ground_truth: Ground-truth dictionary (planted_dependency_groups).
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    if dep_df.empty or "supplier_dependency_ratio" not in dep_df.columns:
        return go.Figure()

    mfg = dep_df[dep_df["node_type"] == "manufacturer"]
    planted: set[str] = set()
    for group in (ground_truth or {}).get("planted_dependency_groups", []):
        planted.update(group.get("dependent_manufacturers", []))
    is_planted = mfg["node"].isin(planted)

    bins = dict(start=0.0, end=1.0001, size=0.05)
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=mfg[~is_planted]["supplier_dependency_ratio"], xbins=bins, name="Other manufacturers",
        marker=dict(color=OTHER_COLOR, line=dict(color=SURFACE, width=2)),
        hovertemplate="ratio %{x}<br>%{y} manufacturers<extra></extra>",
    ))
    if is_planted.any():
        fig.add_trace(go.Histogram(
            x=mfg[is_planted]["supplier_dependency_ratio"], xbins=bins, name="Planted dependent manufacturers",
            marker=dict(color=CATEGORICAL[1], line=dict(color=SURFACE, width=2)),
            hovertemplate="ratio %{x}<br>%{y} planted manufacturers<extra></extra>",
        ))
    _style(fig, "Supplier dependency ratio of manufacturers", height=500)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Share of inbound volume from the largest supplier", range=[0, 1])
    fig.update_yaxes(title_text="Number of manufacturers")
    if output_dir:
        save_figure(fig, output_dir / "dependency_concentration", ["png"])
    return fig


def plot_temporal_metrics(
    snapshot_df: pd.DataFrame,
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot network evolution over time as small multiples (one measure per panel).

    Args:
        snapshot_df: Temporal snapshot DataFrame with per-month statistics.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    if snapshot_df.empty:
        return go.Figure()

    panels = [
        ("num_nodes", "Active organizations"),
        ("num_edges", "Active relationships"),
        ("density", "Density"),
        ("num_communities", "Detected communities"),
        ("modularity", "Modularity"),
        ("global_efficiency", "Global efficiency"),
    ]
    panels = [(c, t) for c, t in panels if c in snapshot_df.columns and snapshot_df[c].notna().any()]
    n_cols = 3
    n_rows = math.ceil(len(panels) / n_cols)
    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=[t for _, t in panels], vertical_spacing=0.16)

    x = pd.to_datetime(snapshot_df["month"])
    for idx, (col, label) in enumerate(panels):
        fig.add_trace(
            go.Scatter(
                x=x, y=snapshot_df[col], mode="lines+markers",
                line=dict(color=SEQUENTIAL_HUE, width=2), marker=dict(size=5),
                hovertemplate="%{x|%b %Y}<br>" + label + ": %{y:.4g}<extra></extra>",
            ),
            row=idx // n_cols + 1, col=idx % n_cols + 1,
        )
        if col == "num_communities":
            fig.update_yaxes(dtick=1, row=idx // n_cols + 1, col=idx % n_cols + 1)
    _style(fig, "Monthly evolution of the network", height=330 * n_rows + 60, width=1200, showlegend=False)
    fig.update_xaxes(tickformat="%b %y", nticks=5)
    if output_dir:
        save_figure(fig, output_dir / "temporal_metrics", ["png"])
    return fig


def plot_resilience_curves(
    resilience_results: dict[str, pd.DataFrame],
    output_dir: Path | None = None,
) -> go.Figure:
    """Plot network degradation curves for all attack strategies.

    Args:
        resilience_results: Dict strategy → DataFrame with resilience metrics.
        output_dir: Directory to save figure.

    Returns:
        Plotly figure.
    """
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Largest connected component", "Global efficiency"])

    for strategy in [s for s in STRATEGY_STYLE if s in resilience_results] + [
        s for s in resilience_results if s not in STRATEGY_STYLE
    ]:
        df = resilience_results[strategy]
        name, color = STRATEGY_STYLE.get(strategy, (_label(strategy), OTHER_COLOR))
        x = df["fraction_removed"]
        y_lcc = df["lcc_mean"] if "lcc_mean" in df.columns else df.get("largest_component_fraction")
        y_eff = df["efficiency_mean"] if "efficiency_mean" in df.columns else df.get("network_efficiency")
        line = dict(color=color, width=2, dash="dash" if strategy == "random" else "solid")

        if y_lcc is not None:
            fig.add_trace(
                go.Scatter(x=x, y=y_lcc, name=name, legendgroup=strategy, line=line, mode="lines+markers",
                           marker=dict(size=8),
                           hovertemplate=name + "<br>%{x:.0%} removed<br>LCC share: %{y:.3f}<extra></extra>"),
                row=1, col=1,
            )
        if y_eff is not None:
            fig.add_trace(
                go.Scatter(x=x, y=y_eff, name=name, legendgroup=strategy, line=line, mode="lines+markers",
                           marker=dict(size=8), showlegend=False,
                           hovertemplate=name + "<br>%{x:.0%} removed<br>Efficiency: %{y:.3f}<extra></extra>"),
                row=1, col=2,
            )

    _style(fig, "Network resilience under random failure and targeted attacks", height=500, width=1200)
    fig.update_xaxes(title_text="Share of organizations removed", tickformat=".0%")
    fig.update_yaxes(title_text="Share of remaining organizations in largest component", row=1, col=1)
    fig.update_yaxes(title_text="Global efficiency", row=1, col=2)
    fig.update_layout(legend=dict(title_text="Removal strategy"))
    if output_dir:
        save_figure(fig, output_dir / "resilience_curves", ["png"])
    return fig


def write_captions(figures_dir: Path) -> None:
    """Write a README.md listing every generated figure with its caption.

    Args:
        figures_dir: Directory containing the figures.
    """
    lines = ["# Figures", "", "Generated by `python -m reports.generate`. Captions describe what each figure shows.", ""]
    number = 1
    for name, caption in CAPTIONS.items():
        if (figures_dir / f"{name}.png").exists():
            lines += [f"## Figure {number}: `{name}.png`", "", caption, ""]
            number += 1
    (figures_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved captions → %s", figures_dir / "README.md")


def generate_all_figures(
    G: nx.DiGraph,
    centrality_df: pd.DataFrame,
    community_df: pd.DataFrame,
    snapshot_df: pd.DataFrame,
    resilience_results: dict[str, pd.DataFrame],
    figures_dir: Path,
    kcore_df: pd.DataFrame | None = None,
    dep_df: pd.DataFrame | None = None,
    ground_truth: dict[str, Any] | None = None,
) -> None:
    """Generate and save all required figures.

    Args:
        G: Directed supply-chain graph.
        centrality_df: Centrality DataFrame.
        community_df: Community DataFrame.
        snapshot_df: Temporal snapshot DataFrame.
        resilience_results: Resilience experiment results.
        figures_dir: Directory to save figures.
        kcore_df: Optional k-core DataFrame.
        dep_df: Optional upstream concentration DataFrame.
        ground_truth: Optional ground-truth dictionary for highlighting planted structures.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generating all figures → %s", figures_dir)

    plot_network_graph(G, centrality_df=centrality_df, output_dir=figures_dir, filename="network_graph")
    if not community_df.empty:
        plot_network_graph(
            G, centrality_df=centrality_df, community_df=community_df,
            output_dir=figures_dir, filename="network_graph_community",
        )
        plot_community_sizes(community_df, output_dir=figures_dir, G=G)
    if not centrality_df.empty:
        plot_degree_distribution(centrality_df, output_dir=figures_dir)
        plot_centrality_comparison(centrality_df, output_dir=figures_dir)
        plot_centrality_heatmap(centrality_df, output_dir=figures_dir)
        plot_bridge_hub_scatter(centrality_df, ground_truth, output_dir=figures_dir)
    if kcore_df is not None and not kcore_df.empty:
        plot_kcore_distribution(kcore_df, output_dir=figures_dir)
    if dep_df is not None and not dep_df.empty:
        plot_dependency_concentration(dep_df, ground_truth, output_dir=figures_dir)
    plot_temporal_metrics(snapshot_df, output_dir=figures_dir)
    plot_resilience_curves(resilience_results, output_dir=figures_dir)

    write_captions(figures_dir)
    logger.info("All figures generated")
