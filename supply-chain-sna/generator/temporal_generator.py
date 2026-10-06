"""
Supply Chain SNA — Temporal Generator
PHASE 4: Generates multi-period snapshots with realistic temporal evolution.

Simulates organizational entry/exit, relationship creation/weakening,
seasonal demand variation, and disruption events.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime
from typing import Any

import pandas as pd

from generator.organization_generator import generate_organizations
from generator.network_generator import _get_relationship_type, generate_network, pick_target
from generator.transaction_generator import generate_transactions, _add_months

logger = logging.getLogger(__name__)


def generate_temporal_dataset(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Generate the full temporal supply-chain dataset.

    Generates organizations, the base network, and transactions for each
    time period. Applies temporal events (org entry/exit, edge changes,
    disruptions, seasonality).

    Args:
        config: Configuration dictionary.

    Returns:
        Tuple of:
            - organizations: DataFrame of all organizations (with status changes)
            - all_transactions: DataFrame of all transactions across all months
            - event_log: DataFrame of all simulated events
            - ground_truth: Ground-truth dictionary with planted structures
    """
    seed: int = config["seed"]
    rng = random.Random(seed + 999)

    n_months: int = config["network"]["months"]
    start_date = datetime.strptime(config["network"]["start_date"], "%Y-%m-%d")

    org_entry_rate: float = config["temporal"]["organization_entry_rate"]
    org_exit_rate: float = config["temporal"]["organization_exit_rate"]
    rel_new_rate: float = config["temporal"]["relationship_new_rate"]
    rel_drop_rate: float = config["temporal"]["relationship_drop_rate"]
    disruption_months: list[int] = config["temporal"]["disruption_months"]
    seasonal_peak_months: list[int] = config["temporal"]["seasonal_peak_months"]

    # Generate base organizations and network
    logger.info("Generating base organizations…")
    organizations, ground_truth = generate_organizations(config)

    logger.info("Generating base network structure…")
    base_edges, ground_truth = generate_network(organizations, ground_truth, config)

    planted_cfg = config.get("planted_structures", {})
    intra_prob: float = planted_cfg.get("intra_community_edge_prob", 0.92)
    dependency_volume_mult: float = planted_cfg.get("dependency_volume_multiplier", 8.0)

    all_org_ids: list[str] = organizations["organization_id"].tolist()
    org_type_map = dict(zip(organizations["organization_id"], organizations["organization_type"]))
    org_region_map = dict(zip(organizations["organization_id"], organizations["region"]))
    type_to_ids: dict[str, list[str]] = {}
    region_type_ids: dict[tuple[str, str], list[str]] = {}
    for oid in all_org_ids:
        type_to_ids.setdefault(org_type_map[oid], []).append(oid)
        region_type_ids.setdefault((org_region_map[oid], org_type_map[oid]), []).append(oid)

    # Planted organizations stay in the network for the whole period so the
    # ground-truth structures exist in every snapshot.
    protected: set[str] = set(ground_truth["planted_hubs"]) | set(ground_truth["planted_bridges"])
    dependency_edges: set[tuple[str, str]] = set()
    for group in ground_truth["planted_dependency_groups"]:
        protected.add(group["critical_supplier"])
        protected.update(group["dependent_manufacturers"])
        for mfg in group["dependent_manufacturers"]:
            dependency_edges.add((group["critical_supplier"], mfg))

    # Late entrants: organizations that join after the first month.
    n_entries_per_month = max(0, round(len(all_org_ids) * org_entry_rate))
    unprotected = [oid for oid in all_org_ids if oid not in protected]
    n_late = min(n_entries_per_month * max(0, n_months - 1), len(unprotected) // 2)
    pending_entrants: list[str] = rng.sample(unprotected, n_late)

    active_orgs = set(all_org_ids) - set(pending_entrants)
    entry_month: dict[str, str] = {}
    exit_month: dict[str, str] = {}

    current_edges = set(zip(base_edges["source_node"], base_edges["target_node"]))
    edge_rel_types = dict(
        zip(
            zip(base_edges["source_node"], base_edges["target_node"]),
            base_edges["relationship_type"],
        )
    )

    all_transactions: list[pd.DataFrame] = []
    event_records: list[dict[str, Any]] = []
    temporal_snapshots: list[dict[str, Any]] = []

    def _log_event(month_date: datetime, month_str: str, event_type: str,
                   org_id: str | None, severity: str, description: str) -> None:
        event_records.append(
            {
                "event_id": f"EVT-{len(event_records)+1:05d}",
                "timestamp": month_date.isoformat(),
                "event_type": event_type,
                "organization_id": org_id,
                "target_id": None,
                "severity": severity,
                "description": description,
                "month": month_str,
            }
        )

    for month_idx in range(n_months):
        month_date = _add_months(start_date, month_idx)
        month_str = month_date.strftime("%Y-%m")
        month_of_year = month_date.month

        logger.info("Processing month %s (index %d/%d)…", month_str, month_idx + 1, n_months)

        is_disruption = (month_idx + 1) in disruption_months
        is_seasonal_peak = month_of_year in seasonal_peak_months

        if month_idx > 0:
            # ── Org entries ──────────────────────────────────────────────────
            for org_id in pending_entrants[:n_entries_per_month]:
                active_orgs.add(org_id)
                entry_month[org_id] = month_str
                _log_event(month_date, month_str, "organization_entry", org_id, "low",
                           f"{org_id} joined the network in {month_str}")
            pending_entrants = pending_entrants[n_entries_per_month:]

            # ── Org exits ────────────────────────────────────────────────────
            exit_candidates = sorted(active_orgs - protected)
            n_exits = min(max(0, round(len(active_orgs) * org_exit_rate)), len(exit_candidates))
            for org_id in rng.sample(exit_candidates, n_exits):
                active_orgs.discard(org_id)
                exit_month[org_id] = month_str
                current_edges = {(s, t) for s, t in current_edges if s != org_id and t != org_id}
                _log_event(month_date, month_str, "organization_exit", org_id, "medium",
                           f"{org_id} became inactive in {month_str}")

            # ── Edge drops ───────────────────────────────────────────────────
            droppable = sorted(current_edges - dependency_edges)
            n_edge_drops = min(max(0, round(len(current_edges) * rel_drop_rate)), len(droppable))
            for edge in rng.sample(droppable, n_edge_drops):
                current_edges.discard(edge)

        # ── Active edges for this month ──────────────────────────────────────
        active_edges = sorted(
            (s, t) for s, t in current_edges if s in active_orgs and t in active_orgs
        )

        # ── Volume multipliers ───────────────────────────────────────────────
        event_mults: dict[str, float] = {
            f"{s}→{t}": dependency_volume_mult for s, t in dependency_edges
        }
        if is_disruption and active_edges:
            disrupted_edges = rng.sample(active_edges, max(1, len(active_edges) // 10))
            for s, t in disrupted_edges:
                key = f"{s}→{t}"
                event_mults[key] = event_mults.get(key, 1.0) * 0.2
            _log_event(month_date, month_str, "disruption", None, "high",
                       f"Supply disruption in month {month_str}: {len(disrupted_edges)} edges impacted")
        if is_seasonal_peak:
            for s, t in active_edges:
                key = f"{s}→{t}"
                event_mults[key] = event_mults.get(key, 1.0) * 1.5

        active_edges_df = pd.DataFrame(
            [
                {
                    "source_node": s,
                    "target_node": t,
                    "relationship_type": edge_rel_types.get((s, t), "supply_chain_link"),
                }
                for s, t in active_edges
            ],
            columns=["source_node", "target_node", "relationship_type"],
        )

        # ── Generate transactions for this month ─────────────────────────────
        if not active_edges_df.empty:
            month_txns = generate_transactions(
                active_edges_df,
                organizations[organizations["organization_id"].isin(active_orgs)],
                config,
                month_offset=month_idx,
                event_multipliers=event_mults,
            )
            all_transactions.append(month_txns)

        temporal_snapshots.append(
            {
                "month": month_str,
                "month_index": month_idx,
                "active_orgs": len(active_orgs),
                "active_edges": len(active_edges),
                "is_disruption": is_disruption,
                "is_seasonal_peak": is_seasonal_peak,
            }
        )

        # ── New relationships (take effect next month) ───────────────────────
        n_new_edges = max(0, round(len(active_edges) * rel_new_rate))
        active_org_list = sorted(active_orgs)
        for _ in range(n_new_edges):
            if len(active_org_list) < 2:
                break
            src = rng.choice(active_org_list)
            tgt = pick_target(
                src, rng, org_type_map, org_region_map, type_to_ids, region_type_ids,
                intra_prob=intra_prob, active=active_orgs,
            )
            if tgt is not None and (src, tgt) not in current_edges:
                current_edges.add((src, tgt))
                edge_rel_types[(src, tgt)] = _get_relationship_type(
                    org_type_map.get(src, ""), org_type_map.get(tgt, "")
                )

    # ── Record lifecycle on the organization table ───────────────────────────
    organizations = organizations.copy()
    never_joined = set(pending_entrants)
    organizations["entry_month"] = organizations["organization_id"].map(entry_month)
    organizations["exit_month"] = organizations["organization_id"].map(exit_month)
    organizations["status"] = [
        "inactive" if (oid in exit_month or oid in never_joined) else "active"
        for oid in organizations["organization_id"]
    ]

    combined_transactions = pd.concat(all_transactions, ignore_index=True) if all_transactions else pd.DataFrame()
    event_log = pd.DataFrame(event_records) if event_records else pd.DataFrame()

    ground_truth["temporal_snapshots"] = temporal_snapshots

    logger.info(
        "Temporal generation complete: %d total transactions across %d months",
        len(combined_transactions),
        n_months,
    )

    return organizations, combined_transactions, event_log, ground_truth
