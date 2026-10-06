"""
Supply Chain SNA — Organization Generator
PHASE 1: Generates realistic supply-chain organizations with typed IDs,
regions, industries, sizes, and statuses.
"""
from __future__ import annotations

import logging
import random
from typing import Any

import pandas as pd
from faker import Faker

logger = logging.getLogger(__name__)

# Maps org type abbreviation to full name
ORG_TYPE_PREFIXES: dict[str, str] = {
    "supplier": "SUP",
    "manufacturer": "MFG",
    "distributor": "DST",
    "warehouse": "WHS",
    "logistics_provider": "LOG",
    "retailer": "RET",
}


def generate_organizations(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Generate a synthetic set of supply-chain organizations.

    Args:
        config: Configuration dictionary loaded from YAML.

    Returns:
        Tuple of (organizations_dataframe, ground_truth_dict).
        organizations_dataframe columns:
            organization_id, organization_name, organization_type,
            region, industry, size_category, status, created_at
        ground_truth_dict contains:
            planted_hubs, planted_bridges, planted_dependency_groups,
            planted_communities (region → list of org_ids)
    """
    seed: int = config["seed"]
    rng = random.Random(seed)
    fake = Faker()
    Faker.seed(seed)

    n_orgs: int = config["network"]["organizations"]
    org_type_dist: dict[str, float] = config["organization_types"]
    regions: list[str] = config["regions"]
    industries: list[str] = config["industries"]
    size_categories: list[str] = config["size_categories"]
    start_date: str = config["network"]["start_date"]

    planted_cfg = config.get("planted_structures", {})
    num_hubs: int = planted_cfg.get("num_hubs", 5)
    num_bridges: int = planted_cfg.get("num_bridges", 10)
    num_dependency_groups: int = planted_cfg.get("num_dependency_groups", 3)

    logger.info("Generating %d organizations (seed=%d)…", n_orgs, seed)

    # Determine counts per type
    type_counts: dict[str, int] = {}
    remaining = n_orgs
    types = list(org_type_dist.keys())
    for i, otype in enumerate(types):
        if i == len(types) - 1:
            type_counts[otype] = remaining
        else:
            count = max(1, round(org_type_dist[otype] * n_orgs))
            type_counts[otype] = count
            remaining -= count

    # Build organization list
    records: list[dict[str, Any]] = []
    type_counters: dict[str, int] = {t: 0 for t in types}

    for otype, count in type_counts.items():
        prefix = ORG_TYPE_PREFIXES[otype]
        for _ in range(count):
            type_counters[otype] += 1
            org_id = f"{prefix}-{type_counters[otype]:05d}"
            region = rng.choice(regions)
            industry = rng.choice(industries)
            size = rng.choice(size_categories)

            # Generate realistic company name
            company_name = fake.company()

            records.append(
                {
                    "organization_id": org_id,
                    "organization_name": company_name,
                    "organization_type": otype,
                    "region": region,
                    "industry": industry,
                    "size_category": size,
                    "status": "active",
                    "created_at": start_date,
                }
            )

    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    # ── Plant known structural roles ──────────────────────────────────────────
    all_ids = df["organization_id"].tolist()

    # Hubs: prefer manufacturers and distributors (high connectivity)
    hub_candidates = df[df["organization_type"].isin(["manufacturer", "distributor"])][
        "organization_id"
    ].tolist()
    planted_hubs = rng.sample(hub_candidates, min(num_hubs, len(hub_candidates)))

    # Bridges: distributors and warehouses. Both receive goods and pass them
    # on, so they can sit *between* regions. (Logistics providers have no
    # inbound edges in this model, so they can never lie on a shortest path.)
    bridge_candidates = df[
        df["organization_type"].isin(["distributor", "warehouse"])
        & ~df["organization_id"].isin(planted_hubs)
    ]["organization_id"].tolist()
    planted_bridges = rng.sample(bridge_candidates, min(num_bridges, len(bridge_candidates)))

    # Communities: map region → org_ids
    planted_communities: dict[str, list[str]] = {}
    for region in regions:
        planted_communities[region] = df[df["region"] == region]["organization_id"].tolist()

    # Dependency groups: one critical supplier that several manufacturers
    # rely on for most of their inbound volume (a hidden common dependency).
    taken = set(planted_hubs) | set(planted_bridges)
    supplier_ids = [
        s for s in df[df["organization_type"] == "supplier"]["organization_id"].tolist()
    ]
    manufacturer_ids = [
        m for m in df[df["organization_type"] == "manufacturer"]["organization_id"].tolist()
        if m not in taken
    ]
    group_size: int = planted_cfg.get("dependency_group_size", 5)
    n_groups = min(num_dependency_groups, len(supplier_ids), len(manufacturer_ids) // max(1, group_size))
    critical_suppliers = rng.sample(supplier_ids, n_groups)
    dependent_pool = rng.sample(manufacturer_ids, n_groups * group_size)
    dependency_groups: list[dict[str, Any]] = []
    for i, supplier in enumerate(critical_suppliers):
        dependency_groups.append(
            {
                "group_id": f"DEP-{i+1:03d}",
                "critical_supplier": supplier,
                "dependent_manufacturers": dependent_pool[i * group_size:(i + 1) * group_size],
            }
        )

    ground_truth: dict[str, Any] = {
        "planted_hubs": planted_hubs,
        "planted_bridges": planted_bridges,
        "planted_communities": planted_communities,
        "planted_dependency_groups": dependency_groups,
    }

    logger.info(
        "Generated %d organizations: %s",
        len(df),
        {t: c for t, c in type_counts.items()},
    )
    logger.info(
        "Ground truth — hubs: %d, bridges: %d, communities: %d, dep_groups: %d",
        len(planted_hubs),
        len(planted_bridges),
        len(planted_communities),
        len(dependency_groups),
    )

    return df, ground_truth
