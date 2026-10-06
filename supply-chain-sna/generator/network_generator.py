"""
Supply Chain SNA — Network Generator
PHASE 2: Generates realistic supply-chain network relationships.

Uses hierarchical supply-chain constraints, planted hubs, bridges,
communities, and dependency groups to create a structurally realistic
directed graph rather than a uniformly random graph.
"""
from __future__ import annotations

import logging
import random
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Valid supply-chain edges by organization type
ALLOWED_EDGES: dict[str, list[str]] = {
    "supplier": ["manufacturer", "warehouse"],
    "manufacturer": ["distributor", "warehouse", "retailer"],
    "distributor": ["retailer", "warehouse"],
    "warehouse": ["distributor", "retailer", "manufacturer"],
    "logistics_provider": ["supplier", "manufacturer", "distributor", "warehouse", "retailer"],
    "retailer": [],  # retailers are sinks (endpoints)
}


def generate_network(
    organizations: pd.DataFrame,
    ground_truth: dict[str, Any],
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Generate a directed supply-chain network with planted structures.

    Args:
        organizations: DataFrame of organizations from organization_generator.
        ground_truth: Ground-truth dictionary with planted hubs/bridges/etc.
        config: Configuration dictionary.

    Returns:
        Tuple of (edges_dataframe, updated_ground_truth).
        edges_dataframe columns:
            source_node, target_node, relationship_type, weight_seed
    """
    seed: int = config["seed"]
    rng = random.Random(seed + 1)  # offset to avoid org-gen correlation

    planted_cfg = config.get("planted_structures", {})
    hub_multiplier: float = planted_cfg.get("hub_connectivity_multiplier", 5.0)
    bridge_regions: int = planted_cfg.get("bridge_inter_community_links", 4)
    bridge_links_per_region: int = planted_cfg.get("bridge_links_per_community", 8)
    bridge_inbound_links: int = planted_cfg.get("bridge_inbound_links", 6)
    intra_prob: float = planted_cfg.get("intra_community_edge_prob", 0.92)
    target_edges: int = config["network"].get("target_edges", 5000)

    planted_hubs: list[str] = ground_truth["planted_hubs"]
    planted_bridges: list[str] = ground_truth["planted_bridges"]
    planted_communities: dict[str, list[str]] = ground_truth["planted_communities"]
    dependency_groups: list[dict[str, Any]] = ground_truth["planted_dependency_groups"]

    # Build type → org_id lookup
    type_to_ids: dict[str, list[str]] = {}
    for _, row in organizations.iterrows():
        otype = row["organization_type"]
        type_to_ids.setdefault(otype, []).append(row["organization_id"])

    org_type: dict[str, str] = dict(
        zip(organizations["organization_id"], organizations["organization_type"])
    )
    org_region: dict[str, str] = dict(
        zip(organizations["organization_id"], organizations["region"])
    )

    edges: set[tuple[str, str]] = set()

    # ── 1. Intra-community edges (hierarchical flow within regions) ───────────
    for region, region_orgs in planted_communities.items():
        region_type_map: dict[str, list[str]] = {}
        for oid in region_orgs:
            otype = org_type.get(oid, "")
            region_type_map.setdefault(otype, []).append(oid)

        # Connect hierarchically within region
        _add_hierarchical_edges(region_type_map, edges, rng, prefer_regional=True)

    # ── 2. Hub nodes: greatly expanded connectivity ───────────────────────────
    for hub_id in planted_hubs:
        hub_type = org_type.get(hub_id, "")
        targets = ALLOWED_EDGES.get(hub_type, [])
        for target_type in targets:
            candidates = [
                oid for oid in type_to_ids.get(target_type, []) if oid != hub_id
            ]
            n_connections = min(int(len(candidates) * 0.2 * hub_multiplier / 10), len(candidates))
            n_connections = max(n_connections, 5)
            chosen = rng.sample(candidates, min(n_connections, len(candidates)))
            for target in chosen:
                edges.add((hub_id, target))

    # ── 3. Bridge nodes: gateways between communities ─────────────────────────
    # A bridge collects goods inside its own region and ships them to several
    # organizations in other regions, so cross-region paths run through it.
    region_list = list(planted_communities.keys())
    for bridge_id in planted_bridges:
        bridge_region = org_region.get(bridge_id, "")
        bridge_type = org_type.get(bridge_id, "")

        inbound_types = [
            t for t, targets in ALLOWED_EDGES.items()
            if bridge_type in targets and t != "logistics_provider"
        ]
        inbound_candidates = [
            oid
            for oid in planted_communities.get(bridge_region, [])
            if org_type.get(oid, "") in inbound_types and oid != bridge_id
        ]
        for source in rng.sample(inbound_candidates, min(bridge_inbound_links, len(inbound_candidates))):
            edges.add((source, bridge_id))

        other_regions = [r for r in region_list if r != bridge_region]
        rng.shuffle(other_regions)
        for other_region in other_regions[:bridge_regions]:
            other_candidates = [
                oid
                for oid in planted_communities.get(other_region, [])
                if org_type.get(oid, "") in ALLOWED_EDGES.get(bridge_type, [])
            ]
            for target in rng.sample(other_candidates, min(bridge_links_per_region, len(other_candidates))):
                edges.add((bridge_id, target))

    # ── 4. Dependency groups: one critical supplier → several manufacturers ───
    for dep_group in dependency_groups:
        supplier_id = dep_group["critical_supplier"]
        for mfg_id in dep_group["dependent_manufacturers"]:
            edges.add((supplier_id, mfg_id))

    # ── 5. Fill to target_edges ───────────────────────────────────────────────
    # Mostly intra-region (keeps the planted communities visible), with
    # preferential attachment so a few organizations become much better
    # connected than the rest.
    region_type_ids: dict[tuple[str, str], list[str]] = {}
    for oid in organizations["organization_id"].tolist():
        region_type_ids.setdefault((org_region[oid], org_type[oid]), []).append(oid)

    in_degree: dict[str, int] = {}
    for _, t in edges:
        in_degree[t] = in_degree.get(t, 0) + 1

    all_orgs = organizations["organization_id"].tolist()
    attempts = 0
    max_attempts = target_edges * 10
    while len(edges) < target_edges and attempts < max_attempts:
        attempts += 1
        source = rng.choice(all_orgs)
        target = pick_target(
            source, rng, org_type, org_region, type_to_ids, region_type_ids,
            intra_prob=intra_prob, in_degree=in_degree,
        )
        if target is None or (source, target) in edges:
            continue
        edges.add((source, target))
        in_degree[target] = in_degree.get(target, 0) + 1

    logger.info("Generated %d unique directed edges", len(edges))

    edge_records = [
        {
            "source_node": s,
            "target_node": t,
            "relationship_type": _get_relationship_type(org_type.get(s, ""), org_type.get(t, "")),
        }
        for s, t in sorted(edges)
    ]

    edges_df = pd.DataFrame(edge_records)
    return edges_df, ground_truth


def pick_target(
    source: str,
    rng: random.Random,
    org_type: dict[str, str],
    org_region: dict[str, str],
    type_to_ids: dict[str, list[str]],
    region_type_ids: dict[tuple[str, str], list[str]],
    intra_prob: float = 0.92,
    in_degree: dict[str, int] | None = None,
    active: set[str] | None = None,
) -> str | None:
    """Pick a valid downstream partner for ``source``.

    The partner type follows ALLOWED_EDGES. With probability ``intra_prob``
    it is drawn from the source's own region, otherwise from any region.
    If ``in_degree`` is given, candidates are weighted by (in-degree + 1)
    (preferential attachment).

    Args:
        source: Source organization ID.
        rng: Random number generator.
        org_type: Mapping org_id → organization type.
        org_region: Mapping org_id → region.
        type_to_ids: Mapping type → org_ids (all regions).
        region_type_ids: Mapping (region, type) → org_ids.
        intra_prob: Probability of choosing a same-region partner.
        in_degree: Optional current in-degree per org for weighting.
        active: Optional set restricting candidates to active organizations.

    Returns:
        Target organization ID, or None if no valid candidate exists.
    """
    allowed_targets = ALLOWED_EDGES.get(org_type.get(source, ""), [])
    if not allowed_targets:
        return None
    target_type = rng.choice(allowed_targets)
    if rng.random() < intra_prob:
        pool = region_type_ids.get((org_region.get(source, ""), target_type), [])
    else:
        pool = type_to_ids.get(target_type, [])
    candidates = [
        oid for oid in pool if oid != source and (active is None or oid in active)
    ]
    if not candidates:
        return None
    if in_degree is None:
        return rng.choice(candidates)
    weights = [in_degree.get(oid, 0) + 1 for oid in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


def _add_hierarchical_edges(
    region_type_map: dict[str, list[str]],
    edges: set[tuple[str, str]],
    rng: random.Random,
    prefer_regional: bool = True,
) -> None:
    """Add hierarchical supply-chain edges within a region.

    Args:
        region_type_map: Mapping of org_type → list of org_ids in region.
        edges: Set to add new (source, target) tuples to.
        rng: Random number generator.
        prefer_regional: If True, prefer intra-region connections.
    """
    # supplier → manufacturer
    _connect_tier(
        region_type_map.get("supplier", []),
        region_type_map.get("manufacturer", []),
        edges,
        rng,
        min_connections=1,
        max_connections=3,
    )
    # manufacturer → distributor
    _connect_tier(
        region_type_map.get("manufacturer", []),
        region_type_map.get("distributor", []),
        edges,
        rng,
        min_connections=1,
        max_connections=3,
    )
    # distributor → retailer
    _connect_tier(
        region_type_map.get("distributor", []),
        region_type_map.get("retailer", []),
        edges,
        rng,
        min_connections=1,
        max_connections=4,
    )
    # manufacturer → warehouse
    _connect_tier(
        region_type_map.get("manufacturer", []),
        region_type_map.get("warehouse", []),
        edges,
        rng,
        min_connections=0,
        max_connections=2,
    )
    # warehouse → distributor
    _connect_tier(
        region_type_map.get("warehouse", []),
        region_type_map.get("distributor", []),
        edges,
        rng,
        min_connections=0,
        max_connections=2,
    )


def _connect_tier(
    sources: list[str],
    targets: list[str],
    edges: set[tuple[str, str]],
    rng: random.Random,
    min_connections: int,
    max_connections: int,
) -> None:
    """Connect source-tier organizations to target-tier organizations.

    Args:
        sources: List of source organization IDs.
        targets: List of target organization IDs.
        edges: Set to add edges to.
        rng: Random number generator.
        min_connections: Minimum connections per source.
        max_connections: Maximum connections per source.
    """
    if not sources or not targets:
        return
    for src in sources:
        n = rng.randint(min_connections, max_connections)
        if n == 0:
            continue
        chosen = rng.sample(targets, min(n, len(targets)))
        for tgt in chosen:
            edges.add((src, tgt))


def _get_relationship_type(source_type: str, target_type: str) -> str:
    """Return a descriptive relationship type label.

    Args:
        source_type: Organization type of source node.
        target_type: Organization type of target node.

    Returns:
        String label describing the relationship.
    """
    mapping = {
        ("supplier", "manufacturer"): "raw_material_supply",
        ("manufacturer", "distributor"): "product_distribution",
        ("distributor", "retailer"): "retail_distribution",
        ("manufacturer", "warehouse"): "warehouse_storage",
        ("warehouse", "distributor"): "warehouse_to_distribution",
        ("logistics_provider", "supplier"): "logistics_support",
        ("logistics_provider", "manufacturer"): "logistics_support",
        ("logistics_provider", "distributor"): "logistics_support",
    }
    return mapping.get((source_type, target_type), "supply_chain_link")
