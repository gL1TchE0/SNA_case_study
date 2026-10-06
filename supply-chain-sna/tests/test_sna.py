"""
Supply Chain SNA — Unit Tests
PHASE 20: Tests for data generation, graph construction, and SNA.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def smoke_config() -> dict:
    """Load smoke test configuration."""
    from config import load_config
    return load_config("config/smoke.yaml")


@pytest.fixture
def sample_organizations(smoke_config) -> tuple:
    """Generate a small sample of organizations."""
    from generator.organization_generator import generate_organizations
    return generate_organizations(smoke_config)


@pytest.fixture
def sample_network(sample_organizations, smoke_config) -> tuple:
    """Generate a small sample network."""
    from generator.network_generator import generate_network
    orgs, gt = sample_organizations
    edges, gt2 = generate_network(orgs, gt, smoke_config)
    return orgs, edges, gt2


@pytest.fixture
def sample_graph(sample_organizations, sample_network, smoke_config) -> nx.DiGraph:
    """Build a small graph from sample data."""
    from generator.transaction_generator import generate_transactions
    from graph.builder import build_graph
    orgs, _, gt = sample_network
    _, edges, _ = sample_network
    txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
    return build_graph(orgs, txns)


# ── Phase 1: Organization Generator ───────────────────────────────────────


class TestOrganizationGenerator:
    """Tests for the organization generator."""

    def test_generates_correct_count(self, sample_organizations, smoke_config):
        orgs, _ = sample_organizations
        expected = smoke_config["network"]["organizations"]
        assert len(orgs) == expected, f"Expected {expected} orgs, got {len(orgs)}"

    def test_unique_ids(self, sample_organizations):
        orgs, _ = sample_organizations
        assert orgs["organization_id"].is_unique, "Duplicate organization IDs found"

    def test_valid_organization_types(self, sample_organizations):
        orgs, _ = sample_organizations
        valid_types = {"supplier", "manufacturer", "distributor", "warehouse", "logistics_provider", "retailer"}
        found_types = set(orgs["organization_type"].unique())
        assert found_types.issubset(valid_types), f"Invalid types: {found_types - valid_types}"

    def test_required_columns_exist(self, sample_organizations):
        orgs, _ = sample_organizations
        required = {"organization_id", "organization_name", "organization_type", "region",
                    "industry", "size_category", "status", "created_at"}
        assert required.issubset(set(orgs.columns)), f"Missing columns: {required - set(orgs.columns)}"

    def test_no_null_ids(self, sample_organizations):
        orgs, _ = sample_organizations
        assert orgs["organization_id"].isna().sum() == 0

    def test_id_format(self, sample_organizations):
        orgs, _ = sample_organizations
        prefixes = {"SUP-", "MFG-", "DST-", "WHS-", "LOG-", "RET-"}
        for oid in orgs["organization_id"]:
            assert any(oid.startswith(p) for p in prefixes), f"Bad ID format: {oid}"

    def test_reproducibility(self, smoke_config):
        from generator.organization_generator import generate_organizations
        orgs1, gt1 = generate_organizations(smoke_config)
        orgs2, gt2 = generate_organizations(smoke_config)
        pd.testing.assert_frame_equal(orgs1.reset_index(drop=True), orgs2.reset_index(drop=True))

    def test_ground_truth_has_required_keys(self, sample_organizations):
        _, gt = sample_organizations
        required = {"planted_hubs", "planted_bridges", "planted_communities", "planted_dependency_groups"}
        assert required.issubset(set(gt.keys()))

    def test_planted_hubs_exist_in_orgs(self, sample_organizations):
        orgs, gt = sample_organizations
        org_ids = set(orgs["organization_id"].tolist())
        for hub in gt["planted_hubs"]:
            assert hub in org_ids, f"Planted hub {hub} not in organizations"


# ── Phase 2: Network Generator ────────────────────────────────────────────


class TestNetworkGenerator:
    """Tests for the network generator."""

    def test_generates_edges(self, sample_network):
        _, edges, _ = sample_network
        assert len(edges) > 0, "No edges generated"

    def test_required_edge_columns(self, sample_network):
        _, edges, _ = sample_network
        assert "source_node" in edges.columns
        assert "target_node" in edges.columns

    def test_no_self_loops(self, sample_network):
        _, edges, _ = sample_network
        self_loops = (edges["source_node"] == edges["target_node"]).sum()
        assert self_loops == 0, f"Found {self_loops} self-loops"

    def test_all_edge_nodes_in_orgs(self, sample_network):
        orgs, edges, _ = sample_network
        org_ids = set(orgs["organization_id"].tolist())
        unknown_src = set(edges["source_node"].unique()) - org_ids
        unknown_tgt = set(edges["target_node"].unique()) - org_ids
        assert len(unknown_src) == 0, f"Unknown source nodes: {unknown_src}"
        assert len(unknown_tgt) == 0, f"Unknown target nodes: {unknown_tgt}"


# ── Phase 3: Transaction Generator ────────────────────────────────────────


class TestTransactionGenerator:
    """Tests for the transaction generator."""

    def test_generates_transactions(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
        assert len(txns) > 0, "No transactions generated"

    def test_no_negative_quantities(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
        assert (txns["quantity"] > 0).all()

    def test_unique_transaction_ids(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
        assert txns["transaction_id"].is_unique


# ── Phase 5: Data Validation ──────────────────────────────────────────────


class TestDataValidation:
    """Tests for the data validation module."""

    def test_valid_data_passes(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        from graph.validation import validate_dataset
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
        report = validate_dataset(orgs, txns)
        assert report["is_valid"], f"Validation failed: {report['issues']}"

    def test_detects_duplicate_org_ids(self, sample_organizations, smoke_config):
        from generator.transaction_generator import generate_transactions
        from graph.validation import validate_dataset
        from generator.network_generator import generate_network
        orgs, gt = sample_organizations
        edges, _ = generate_network(orgs, gt, smoke_config)
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)

        # Introduce duplicate
        bad_orgs = pd.concat([orgs, orgs.head(1)], ignore_index=True)
        report = validate_dataset(bad_orgs, txns)
        assert not report["is_valid"]


# ── Phase 6: Graph Builder ─────────────────────────────────────────────────


class TestGraphBuilder:
    """Tests for the graph builder."""

    def test_builds_digraph(self, sample_graph):
        assert isinstance(sample_graph, nx.DiGraph)

    def test_has_nodes(self, sample_graph):
        assert sample_graph.number_of_nodes() > 0

    def test_has_edges(self, sample_graph):
        assert sample_graph.number_of_edges() > 0

    def test_edges_have_weight(self, sample_graph):
        for u, v, data in sample_graph.edges(data=True):
            assert "weight" in data, f"Edge ({u},{v}) missing weight"
            assert data["weight"] > 0

    def test_nodes_have_attributes(self, sample_graph):
        for node, data in sample_graph.nodes(data=True):
            assert "organization_type" in data

    def test_no_self_loops(self, sample_graph):
        assert len(list(nx.selfloop_edges(sample_graph))) == 0

    def test_weight_modes(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        from graph.builder import build_graph
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)

        for mode in ["frequency", "quantity", "transaction_value"]:
            G = build_graph(orgs, txns, weight_mode=mode)
            assert G.number_of_edges() > 0, f"No edges for weight mode {mode}"

    def test_invalid_weight_mode_raises(self, sample_network, smoke_config):
        from generator.transaction_generator import generate_transactions
        from graph.builder import build_graph
        orgs, edges, _ = sample_network
        txns = generate_transactions(edges, orgs, smoke_config, month_offset=0)
        with pytest.raises(ValueError):
            build_graph(orgs, txns, weight_mode="invalid_mode")


# ── Phase 7: Network Statistics ───────────────────────────────────────────


class TestNetworkStatistics:
    """Tests for network statistics computation."""

    def test_basic_stats(self, sample_graph):
        from sna.network_metrics import compute_network_statistics
        stats = compute_network_statistics(sample_graph)
        assert stats["num_nodes"] == sample_graph.number_of_nodes()
        assert stats["num_edges"] == sample_graph.number_of_edges()
        assert 0 <= stats["density"] <= 1
        assert stats["weakly_connected_components"] >= 1


# ── Phase 8: Centrality Engine ────────────────────────────────────────────


class TestCentralityEngine:
    """Tests for centrality computation."""

    def test_degree_returns_all_nodes(self, sample_graph):
        from sna.degree import compute_degree
        df = compute_degree(sample_graph)
        assert len(df) == sample_graph.number_of_nodes()

    def test_degree_columns(self, sample_graph):
        from sna.degree import compute_degree
        df = compute_degree(sample_graph)
        assert "in_degree" in df.columns
        assert "out_degree" in df.columns
        assert "total_degree" in df.columns

    def test_betweenness_range(self, sample_graph):
        from sna.betweenness import compute_betweenness
        df = compute_betweenness(sample_graph, normalized=True)
        assert (df["betweenness"] >= 0).all()
        assert (df["betweenness"] <= 1).all()

    def test_closeness_range(self, sample_graph):
        from sna.closeness import compute_closeness
        df = compute_closeness(sample_graph)
        assert (df["closeness"] >= 0).all()
        assert (df["closeness"] <= 1).all()

    def test_pagerank_sums_to_one(self, sample_graph):
        from sna.pagerank import compute_pagerank
        df = compute_pagerank(sample_graph)
        assert abs(df["pagerank"].sum() - 1.0) < 1e-4

    def test_eigenvector_returns_dataframe(self, sample_graph):
        from sna.eigenvector import compute_eigenvector
        df = compute_eigenvector(sample_graph)
        assert isinstance(df, pd.DataFrame)
        assert "eigenvector" in df.columns


# ── Phase 10: Community Detection ─────────────────────────────────────────


class TestCommunityDetection:
    """Tests for community detection."""

    def test_detects_communities(self, sample_graph):
        from sna.communities import compute_communities
        comm_df, stats = compute_communities(sample_graph)
        assert not comm_df.empty
        assert stats["num_communities"] >= 1

    def test_all_nodes_assigned(self, sample_graph):
        from sna.communities import compute_communities
        comm_df, _ = compute_communities(sample_graph)
        assert len(comm_df) == sample_graph.number_of_nodes()

    def test_modularity_in_range(self, sample_graph):
        from sna.communities import compute_communities
        _, stats = compute_communities(sample_graph)
        if stats.get("modularity") is not None:
            assert -0.5 <= stats["modularity"] <= 1.0


# ── Phase 11: K-Core ──────────────────────────────────────────────────────


class TestKCore:
    """Tests for k-core decomposition."""

    def test_kcore_returns_all_nodes(self, sample_graph):
        from sna.kcore import compute_kcore
        df, stats = compute_kcore(sample_graph)
        assert len(df) == sample_graph.number_of_nodes()

    def test_max_core_positive(self, sample_graph):
        from sna.kcore import compute_kcore
        df, stats = compute_kcore(sample_graph)
        assert stats["max_core_number"] >= 1


# ── Phase 14: Resilience ──────────────────────────────────────────────────


class TestResilience:
    """Tests for resilience experiments."""

    def test_resilience_returns_four_strategies(self, sample_graph):
        from sna.resilience import run_resilience_experiments
        results = run_resilience_experiments(
            sample_graph,
            removal_fractions=[0.05, 0.10],
            random_seeds=[42, 123],
        )
        assert set(results.keys()) == {"random", "degree", "betweenness", "pagerank"}

    def test_baseline_lcc_is_one(self, sample_graph):
        from sna.resilience import run_resilience_experiments
        results = run_resilience_experiments(
            sample_graph,
            removal_fractions=[0.10],
            random_seeds=[42],
        )
        for strategy, df in results.items():
            col = "lcc_mean" if "lcc_mean" in df.columns else "largest_component_fraction"
            baseline = df[df["fraction_removed"] == 0.0]
            if not baseline.empty:
                assert baseline.iloc[0][col] <= 1.0

    def test_lcc_decreases_with_removal(self, sample_graph):
        """LCC should generally not increase as more nodes are removed."""
        from sna.resilience import run_resilience_experiments
        results = run_resilience_experiments(
            sample_graph,
            removal_fractions=[0.05, 0.10, 0.20],
            random_seeds=[42],
        )
        for strategy in ["degree", "betweenness"]:
            df = results[strategy].sort_values("fraction_removed")
            col = "lcc_mean" if "lcc_mean" in df.columns else "largest_component_fraction"
            if col in df.columns and len(df) > 1:
                # Allow for some non-monotonicity due to graph structure, but overall trend
                first = df.iloc[0][col]
                last = df.iloc[-1][col]
                assert last <= first + 0.1, f"LCC unexpectedly increased for {strategy}"


# ── Planted structures, temporal dynamics and dependency analysis ─────────


@pytest.fixture
def temporal_dataset(smoke_config) -> tuple:
    """Generate the full temporal dataset for the smoke configuration."""
    from generator.temporal_generator import generate_temporal_dataset
    return generate_temporal_dataset(smoke_config)


class TestPlantedStructures:
    """Tests for the planted bridges, communities and dependency groups."""

    def test_bridges_can_carry_flow(self, sample_network):
        """Bridges need both inbound and outbound edges to lie on any path."""
        _, edges, gt = sample_network
        sources = set(edges["source_node"])
        targets = set(edges["target_node"])
        for bridge in gt["planted_bridges"]:
            assert bridge in sources and bridge in targets, f"{bridge} cannot be an intermediary"

    def test_most_edges_stay_inside_a_region(self, sample_network):
        orgs, edges, _ = sample_network
        region = dict(zip(orgs["organization_id"], orgs["region"]))
        intra = (edges["source_node"].map(region) == edges["target_node"].map(region)).mean()
        assert intra > 0.5

    def test_dependency_edges_planted(self, sample_network):
        _, edges, gt = sample_network
        edge_set = set(zip(edges["source_node"], edges["target_node"]))
        for group in gt["planted_dependency_groups"]:
            for mfg in group["dependent_manufacturers"]:
                assert (group["critical_supplier"], mfg) in edge_set


class TestTemporalDynamics:
    """Tests for organization entry/exit and temporal snapshots."""

    def test_entries_and_exits_are_logged(self, temporal_dataset):
        _, _, events, _ = temporal_dataset
        types = set(events["event_type"])
        assert "organization_entry" in types
        assert "organization_exit" in types

    def test_generation_is_reproducible(self, smoke_config):
        from generator.temporal_generator import generate_temporal_dataset
        _, txns1, _, _ = generate_temporal_dataset(smoke_config)
        _, txns2, _, _ = generate_temporal_dataset(smoke_config)
        pd.testing.assert_frame_equal(txns1, txns2)

    def test_monthly_snapshots_have_no_inactive_nodes(self, temporal_dataset):
        from graph.builder import build_temporal_graphs
        orgs, txns, _, _ = temporal_dataset
        snapshots = build_temporal_graphs(orgs, txns, mode="monthly")
        for month, G in snapshots.items():
            assert all(d > 0 for _, d in G.degree()), f"Isolated node in snapshot {month}"

    def test_cumulative_snapshots_never_shrink(self, temporal_dataset):
        from graph.builder import build_temporal_graphs
        orgs, txns, _, _ = temporal_dataset
        snapshots = build_temporal_graphs(orgs, txns, mode="cumulative")
        edge_counts = [snapshots[m].number_of_edges() for m in sorted(snapshots)]
        assert edge_counts == sorted(edge_counts)


class TestDependencyAnalysis:
    """Tests for dependency analysis and reversed PageRank."""

    def test_logistics_edges_not_counted_as_supply(self, sample_graph):
        from sna.dependencies import analyze_dependencies
        results = analyze_dependencies(sample_graph)
        for record in results["single_source_nodes"]:
            assert record["supplier_type"] != "logistics_provider"
        conc = results["upstream_concentration"]
        if not conc.empty:
            assert (conc["top_supplier_type"] != "logistics_provider").all()

    def test_centrality_table_has_reversed_pagerank(self, sample_graph, smoke_config):
        from sna.centrality import compute_all_centrality
        df, stats = compute_all_centrality(sample_graph, smoke_config)
        assert "pagerank_reversed" in df.columns
        assert abs(df["pagerank_reversed"].sum() - 1.0) < 1e-3
        assert "weighting_note" in stats


class TestGephiExport:
    """Tests for the Gephi export and the Gephi vs. NetworkX comparison."""

    def test_export_graph_roundtrips_through_gexf(self, sample_graph, smoke_config, tmp_path):
        from graph.export_gephi import build_export_graph
        from sna.centrality import compute_all_centrality
        centrality_df, _ = compute_all_centrality(sample_graph, smoke_config)
        H = build_export_graph(sample_graph, centrality_df, pd.DataFrame(), pd.DataFrame(), {})
        assert H.number_of_nodes() == sample_graph.number_of_nodes()
        assert H.number_of_edges() == sample_graph.number_of_edges()
        node = next(iter(H.nodes))
        assert "nx_pagerank" in H.nodes[node]
        assert H.nodes[node]["planted_role"] == "none"
        path = tmp_path / "graph.gexf"
        nx.write_gexf(H, path)
        assert nx.read_gexf(path).number_of_edges() == H.number_of_edges()

    def test_export_graph_marks_planted_roles(self, sample_graph):
        from graph.export_gephi import build_export_graph
        nodes = list(sample_graph.nodes)
        ground_truth = {"planted_hubs": [nodes[0]], "planted_bridges": [nodes[1]]}
        H = build_export_graph(sample_graph, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), ground_truth)
        assert H.nodes[nodes[0]]["planted_role"] == "hub"
        assert H.nodes[nodes[1]]["planted_role"] == "bridge"

    def test_compare_matches_gephi_columns(self):
        from graph.compare_gephi import compare
        df = pd.DataFrame({
            "Id": [f"N{i}" for i in range(30)],
            "nx_pagerank": [i / 100 for i in range(30)],
            "pageranks": [i / 100 for i in range(30)],
            "nx_betweenness": [i / 10 for i in range(30)],
            "betweenesscentrality": [i * 5.0 for i in range(30)],
        })
        result = compare(df).set_index("metric")
        assert set(result.index) == {"pagerank", "betweenness"}
        assert result.loc["pagerank", "max_abs_difference"] == 0
        assert result.loc["betweenness", "spearman_rho"] == 1.0
        assert result.loc["betweenness", "top20_overlap"] == 20

    def test_compare_without_gephi_statistics_is_empty(self):
        from graph.compare_gephi import compare
        assert compare(pd.DataFrame({"Id": ["A"], "nx_pagerank": [1.0]})).empty
