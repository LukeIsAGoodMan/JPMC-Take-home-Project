"""
profile_jsonl.py — Profile a JSONL census dataset and write a markdown summary.

Usage:
    python profile_jsonl.py --input sample_stratified.jsonl --output summary_report_sample.md
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# --- Constants ---

MISSING_SENTINELS = {"", "?", "Not in universe"}
TARGET_COL = "label"
WEIGHT_COL = "weight"
YEAR_COL = "year"

# Columns we know are numeric (could parse as float)
# but we infer dynamically below instead of hardcoding.


def parse_args():
    p = argparse.ArgumentParser(description="Profile a JSONL census dataset.")
    p.add_argument("--input", required=True, help="Path to input JSONL file")
    p.add_argument("--output", required=True, help="Path to output markdown report")
    return p.parse_args()


def read_jsonl(path: str) -> list[dict]:
    """Read JSONL, skipping malformed lines with a warning."""
    rows = []
    bad = 0
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
                print(f"WARNING: skipped malformed JSON on line {i}", file=sys.stderr)
    if bad:
        print(f"Total malformed lines skipped: {bad}", file=sys.stderr)
    return rows


def is_missing(val: str) -> bool:
    return val in MISSING_SENTINELS


def try_float(val: str):
    """Try to parse a string as float. Returns float or None."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def infer_column_type(col_name: str, values: list[str]) -> str:
    """Classify column role."""
    if col_name == TARGET_COL:
        return "target_categorical"
    if col_name == WEIGHT_COL:
        return "numeric_weight"

    # Check how many non-missing values parse as float
    non_missing = [v for v in values if not is_missing(v)]
    if not non_missing:
        return "categorical_like"

    parseable = sum(1 for v in non_missing if try_float(v) is not None)
    ratio = parseable / len(non_missing)
    # If >=80% of non-missing values are numeric, treat as numeric
    return "numeric_like" if ratio >= 0.8 else "categorical_like"


def profile_numeric(values: list[str]) -> dict:
    """Stats for numeric-like columns (ignoring missing sentinels)."""
    nums = []
    for v in values:
        if is_missing(v):
            continue
        f = try_float(v)
        if f is not None:
            nums.append(f)
    if not nums:
        return {"parseable": 0}
    return {
        "parseable": len(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }


def profile_categorical(values: list[str], top_n: int = 10) -> list[tuple[str, int]]:
    """Top values and counts for categorical columns (including missing sentinels)."""
    return Counter(values).most_common(top_n)


def fmt_num(x, decimals=2) -> str:
    if isinstance(x, int):
        return f"{x:,}"
    return f"{x:,.{decimals}f}"


def build_report(rows: list[dict], input_path: str) -> str:
    """Build the full markdown report string."""
    n_rows = len(rows)
    columns = list(rows[0].keys()) if rows else []
    n_cols = len(columns)

    # Collect per-column values
    col_values = {c: [row.get(c, "") for row in rows] for c in columns}

    # Infer types
    col_types = {c: infer_column_type(c, col_values[c]) for c in columns}

    # --- Label distribution ---
    label_counts = Counter(col_values[TARGET_COL])

    # Weighted label distribution
    weighted_label = Counter()
    for row in rows:
        lbl = row.get(TARGET_COL, "")
        w = try_float(row.get(WEIGHT_COL, "0")) or 0.0
        weighted_label[lbl] += w

    # --- Year distribution ---
    year_counts = Counter(col_values[YEAR_COL])

    # --- Build markdown ---
    lines = []
    a = lines.append

    a(f"# Dataset Profile Report")
    a(f"")
    a(f"**Source**: `{input_path}`  ")
    a(f"**Rows**: {fmt_num(n_rows)}  ")
    a(f"**Columns**: {n_cols}")
    a("")

    # Label distribution
    a("## Label Distribution (Raw Counts)")
    a("")
    a("| Label | Count | % |")
    a("|-------|------:|--:|")
    for lbl, cnt in label_counts.most_common():
        a(f"| `{lbl}` | {fmt_num(cnt)} | {cnt/n_rows*100:.1f}% |")
    a("")

    a("## Label Distribution (Weighted)")
    a("")
    total_w = sum(weighted_label.values())
    a("| Label | Weighted Sum | Weighted % |")
    a("|-------|-------------:|-----------:|")
    for lbl, wsum in weighted_label.most_common():
        a(f"| `{lbl}` | {fmt_num(wsum)} | {wsum/total_w*100:.1f}% |")
    a("")

    # Year distribution
    a("## Year Distribution")
    a("")
    a("| Year | Count | % |")
    a("|------|------:|--:|")
    for yr, cnt in sorted(year_counts.items()):
        a(f"| {yr} | {fmt_num(cnt)} | {cnt/n_rows*100:.1f}% |")
    a("")

    # Column type summary
    a("## Column Types")
    a("")
    a("| # | Column | Inferred Type |")
    a("|---|--------|---------------|")
    for i, c in enumerate(columns, 1):
        a(f"| {i} | {c} | {col_types[c]} |")
    a("")

    # Per-column details
    a("## Per-Column Profile")
    a("")
    for c in columns:
        vals = col_values[c]
        ctype = col_types[c]
        missing_cnt = sum(1 for v in vals if is_missing(v))
        missing_pct = missing_cnt / n_rows * 100 if n_rows else 0

        a(f"### {c}")
        a(f"- **Type**: {ctype}")
        a(f"- **Missing-like**: {fmt_num(missing_cnt)} ({missing_pct:.1f}%)")

        if ctype in ("numeric_like", "numeric_weight"):
            stats = profile_numeric(vals)
            a(f"- **Parseable numeric**: {fmt_num(stats['parseable'])}")
            if stats["parseable"] > 0:
                a(f"- **Min**: {fmt_num(stats['min'])}")
                a(f"- **Mean**: {fmt_num(stats['mean'])}")
                a(f"- **Max**: {fmt_num(stats['max'])}")
        else:
            # categorical / target
            top = profile_categorical(vals, top_n=10)
            a(f"- **Unique values**: {len(set(vals))}")
            a(f"- **Top values**:")
            a("")
            a("  | Value | Count |")
            a("  |-------|------:|")
            for val, cnt in top:
                display = val if val else "(empty)"
                a(f"  | {display} | {fmt_num(cnt)} |")

        a("")

    # Interpretation notes
    a("---")
    a("")
    a("## Interpretation Notes")
    a("")
    a("1. **Sample vs. population**: If this report was run on a sample file, "
      "raw proportions may not match the full dataset. Do not treat sample "
      "counts as population-representative.")
    a("2. **Weight column**: The `weight` column represents CPS population "
      "weights. Final model evaluation and any business-facing metrics "
      "(e.g., weighted accuracy, segment sizes) should incorporate these weights.")
    a("3. **Sentinel values**: Values like `?`, `Not in universe`, and empty "
      "strings appear frequently and require deliberate preprocessing decisions "
      "(drop, impute, or encode as a separate category) depending on the column "
      "and modeling approach.")
    a("4. **Label encoding**: The target labels `- 50000.` and `50000+.` "
      "should be mapped to binary 0/1 for classification.")
    a("5. **Year variable**: Two survey years (94/95) are present. Consider "
      "whether to stratify, feature-engineer, or simply include as a covariate.")
    a("")

    return "\n".join(lines)


def main():
    args = parse_args()
    rows = read_jsonl(args.input)
    if not rows:
        print("ERROR: no valid rows found.", file=sys.stderr)
        sys.exit(1)

    report = build_report(rows, args.input)
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"Report written to {args.output} ({len(rows)} rows profiled)")


if __name__ == "__main__":
    main()
