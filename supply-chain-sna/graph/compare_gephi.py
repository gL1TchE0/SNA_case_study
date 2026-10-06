"""
Supply Chain SNA — Gephi Comparison
Compares the statistics Gephi computed with the ones this project computed.

In Gephi: run the statistics, then Data Laboratory → Export table (nodes) to
CSV. Pass that CSV here.

CLI usage:
    python -m graph.compare_gephi data/exports/gephi_statistics.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from scipy import stats as scipy_stats

# Gephi's column names (its own spellings) → this project's exported columns.
GEPHI_TO_NX = {
    "indegree": "nx_in_degree",
    "outdegree": "nx_out_degree",
    "degree": "nx_total_degree",
    "betweenesscentrality": "nx_betweenness",
    "closnesscentrality": "nx_closeness",
    "eigencentrality": "nx_eigenvector",
    "pageranks": "nx_pagerank",
}


def compare(gephi_df: pd.DataFrame) -> pd.DataFrame:
    """Compare Gephi's statistics with the NetworkX columns in the same table.

    Args:
        gephi_df: Node table exported from Gephi's Data Laboratory.

    Returns:
        DataFrame with one row per metric: Spearman rank correlation, top-20
        overlap and largest absolute difference.
    """
    lower = {c.lower().replace(" ", "").replace("-", ""): c for c in gephi_df.columns}
    rows = []
    for gephi_key, nx_col in GEPHI_TO_NX.items():
        nx_key = nx_col.lower().replace(" ", "")
        if gephi_key not in lower or nx_key not in lower:
            continue
        a = pd.to_numeric(gephi_df[lower[gephi_key]], errors="coerce")
        b = pd.to_numeric(gephi_df[lower[nx_key]], errors="coerce")
        mask = a.notna() & b.notna()
        rho = scipy_stats.spearmanr(a[mask], b[mask])[0]
        top_a = set(a[mask].nlargest(20).index)
        top_b = set(b[mask].nlargest(20).index)
        rows.append(
            {
                "metric": nx_col.replace("nx_", ""),
                "gephi_column": lower[gephi_key],
                "spearman_rho": round(float(rho), 4),
                "top20_overlap": len(top_a & top_b),
                "max_abs_difference": float((a[mask] - b[mask]).abs().max()),
            }
        )
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> None:
    """Print and save the Gephi vs. NetworkX comparison.

    Args:
        argv: Optional CLI arguments for testing.
    """
    parser = argparse.ArgumentParser(description="Supply Chain SNA — Gephi Comparison")
    parser.add_argument("gephi_csv", help="Node table exported from Gephi's Data Laboratory")
    parser.add_argument("--output", default="reports/tables/gephi_comparison.csv")
    args = parser.parse_args(argv)

    path = Path(args.gephi_csv)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    gephi_df = pd.read_csv(path)
    result = compare(gephi_df)
    if result.empty:
        print("No matching statistic columns found. Run the statistics in Gephi before exporting.")
        sys.exit(1)

    print(result.to_string(index=False))
    if "modularity_class" in gephi_df.columns and "nx_community" in gephi_df.columns:
        from sklearn.metrics import adjusted_rand_score
        ari = adjusted_rand_score(gephi_df["nx_community"], gephi_df["modularity_class"])
        print(f"\nCommunity agreement (ARI, Gephi modularity_class vs nx_community): {ari:.4f}")
        result.loc[len(result)] = ["community (ARI)", "modularity_class", round(float(ari), 4), None, None]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    print(f"\nSaved → {out}")


if __name__ == "__main__":
    main()
