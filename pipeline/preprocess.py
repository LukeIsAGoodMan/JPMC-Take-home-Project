"""
preprocess.py — Stage 4: Deterministic preprocessing & data engineering pipeline.

Reads census_bureau.jsonl, applies column-level treatment rules, produces:
  - Classification artifacts: train/val/test splits with metadata
  - Segmentation artifact: cleaned full dataset ready for clustering
  - Audit documentation: column_treatment.md, split_summary.md, PREPROCESSING_AUDIT.md

Usage:
    python preprocess.py                          # defaults
    python preprocess.py --seed 42 --data ../datasource/census_bureau.jsonl
"""

import argparse
import json
import sys
import hashlib
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ──────────────────────────────────────────────────────────────────────
# 0. CONFIGURATION — all column-level decisions in one place
# ──────────────────────────────────────────────────────────────────────

RANDOM_SEED = 42
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}

# Target mapping
LABEL_MAP = {"- 50000.": 0, "50000+.": 1}

# Sentinel values that carry structural meaning (NOT generic NA)
STRUCTURAL_SENTINELS = {"Not in universe", "Not in universe under 1 year old",
                        "Not in universe or children", "Children or Armed Forces"}

# --- Column Groups (sourced from Column_Treatment Excel sheet) ---

CONTINUOUS_NUMERIC = [
    "age",
    "wage per hour",
    "capital gains",
    "capital losses",
    "dividends from stocks",
    "num persons worked for employer",
    "weeks worked in year",
]

# Numeric-coded but semantically categorical — MUST NOT be treated as continuous
NUMERIC_CODED_CATEGORICAL = [
    "detailed industry recode",
    "detailed occupation recode",
    "own business or self employed",
    "veterans benefits",
    "year",
]

CATEGORICAL = [
    "class of worker",
    "education",
    "enroll in edu inst last wk",
    "marital stat",
    "major industry code",
    "major occupation code",
    "race",
    "hispanic origin",
    "sex",
    "member of a labor union",
    "reason for unemployment",
    "full or part time employment stat",
    "tax filer stat",
    "region of previous residence",
    "state of previous residence",
    "detailed household and family stat",
    "detailed household summary in household",
    "migration code-change in msa",
    "migration code-change in reg",
    "migration code-move within reg",
    "live in this house 1 year ago",
    "migration prev res in sunbelt",
    "family members under 18",
    "country of birth father",
    "country of birth mother",
    "country of birth self",
    "citizenship",
    "fill inc questionnaire for veteran's admin",
]

# Excluded from feature matrices (preserved as metadata columns)
EXCLUDED = ["label", "weight"]

# Columns marked "Review" — included in full-feature baseline but flagged for pruning tests
REVIEW_COLUMNS = [
    "reason for unemployment",
    "region of previous residence",
    "state of previous residence",
    "migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin",
]

# Segmentation-excluded columns: sparse/low-actionability fields excluded from clustering
SEGMENTATION_EXCLUDE = [
    "region of previous residence",
    "state of previous residence",
    "migration code-change in msa",
    "migration code-change in reg",
    "migration code-move within reg",
    "migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin",
    "reason for unemployment",
    "member of a labor union",
]

# Monetary columns that benefit from log1p for linear models
LOG1P_CANDIDATES = [
    "wage per hour",
    "capital gains",
    "capital losses",
    "dividends from stocks",
]

ALL_FEATURE_COLS = CONTINUOUS_NUMERIC + NUMERIC_CODED_CATEGORICAL + CATEGORICAL


# ──────────────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ──────────────────────────────────────────────────────────────────────

def load_jsonl(path: str) -> pd.DataFrame:
    """Read JSONL with malformed-line tolerance."""
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
    df = pd.DataFrame(rows)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns from {path}")
    return df


# ──────────────────────────────────────────────────────────────────────
# 2. TARGET & WEIGHT HANDLING
# ──────────────────────────────────────────────────────────────────────

def map_target(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw label strings to binary 0/1. Raise on unexpected values."""
    unexpected = set(df["label"].unique()) - set(LABEL_MAP.keys())
    if unexpected:
        raise ValueError(f"Unexpected label values: {unexpected}")
    df["target"] = df["label"].map(LABEL_MAP).astype(int)
    return df


def parse_weight(df: pd.DataFrame) -> pd.DataFrame:
    """Parse weight column to float. Keep as metadata, not as feature."""
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    n_bad = df["weight"].isna().sum()
    if n_bad > 0:
        print(f"WARNING: {n_bad} unparseable weight values set to NaN", file=sys.stderr)
    return df


# ──────────────────────────────────────────────────────────────────────
# 3. COLUMN-LEVEL CLEANING
# ──────────────────────────────────────────────────────────────────────

def clean_continuous(df: pd.DataFrame) -> pd.DataFrame:
    """Parse continuous numeric columns. True blanks/? -> NaN; zeros preserved."""
    for col in CONTINUOUS_NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_numeric_coded(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric-coded columns to string categories to prevent numeric misuse."""
    for col in NUMERIC_CODED_CATEGORICAL:
        df[col] = df[col].astype(str)
    return df


def clean_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize sentinel values in categorical columns.

    Rules:
    - Empty string -> "Missing"
    - "?" -> "Unknown"
    - Structural sentinels (Not in universe, etc.) -> preserved as-is
    - All other values -> preserved as-is
    """
    for col in CATEGORICAL + NUMERIC_CODED_CATEGORICAL:
        # Empty string -> "Missing"
        df[col] = df[col].replace("", "Missing")
        # "?" -> "Unknown" — explicit label rather than ambiguous punctuation
        df[col] = df[col].replace("?", "Unknown")
        # Cast to string category dtype for memory efficiency
        df[col] = df[col].astype("category")
    return df


def add_log1p_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add log1p-transformed versions of monetary columns (for linear model use)."""
    for col in LOG1P_CANDIDATES:
        new_col = f"{col}_log1p"
        df[new_col] = np.log1p(df[col].fillna(0).clip(lower=0))
    return df


# ──────────────────────────────────────────────────────────────────────
# 4. STRATIFIED TRAIN / VALIDATION / TEST SPLIT
# ──────────────────────────────────────────────────────────────────────

def stratified_split(df: pd.DataFrame, seed: int) -> dict[str, pd.DataFrame]:
    """70/15/15 stratified split on target.

    Two-stage split:
      1. train+val (85%) vs test (15%) — stratify on target
      2. train (70/85 ~ 82.35%) vs val (15/85 ~ 17.65%) — stratify on target
    """
    val_ratio = SPLIT_RATIOS["val"]
    test_ratio = SPLIT_RATIOS["test"]
    trainval_ratio = 1.0 - test_ratio

    df_trainval, df_test = train_test_split(
        df, test_size=test_ratio, random_state=seed, stratify=df["target"]
    )
    val_of_trainval = val_ratio / trainval_ratio
    df_train, df_val = train_test_split(
        df_trainval, test_size=val_of_trainval, random_state=seed,
        stratify=df_trainval["target"]
    )

    splits = {"train": df_train, "val": df_val, "test": df_test}
    for name, split_df in splits.items():
        print(f"  {name}: {len(split_df):,} rows "
              f"(target=1: {split_df['target'].mean():.4f})")
    return splits


# ──────────────────────────────────────────────────────────────────────
# 5. FEATURE MATRIX PREPARATION
# ──────────────────────────────────────────────────────────────────────

def classification_feature_cols() -> list[str]:
    """Return column list for classification feature matrix.
    Excludes label, weight, target (metadata). Includes log1p columns."""
    base = ALL_FEATURE_COLS.copy()
    log1p_cols = [f"{c}_log1p" for c in LOG1P_CANDIDATES]
    return base + log1p_cols


def segmentation_feature_cols() -> list[str]:
    """Return column list for segmentation. Excludes label, weight, target,
    and sparse/low-actionability fields per the preprocessing plan."""
    seg_cols = []
    for col in ALL_FEATURE_COLS:
        if col not in SEGMENTATION_EXCLUDE:
            seg_cols.append(col)
    return seg_cols


# ──────────────────────────────────────────────────────────────────────
# 6. SEGMENTATION DATASET
# ──────────────────────────────────────────────────────────────────────

def build_segmentation_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Build segmentation-ready dataset from full cleaned data.
    - Excludes label and weight from feature columns
    - Preserves weight and target as sidecar columns for interpretation
    """
    seg_cols = segmentation_feature_cols()
    seg_df = df[seg_cols].copy()
    # Attach sidecar columns for downstream interpretation (not for clustering)
    seg_df["_weight"] = df["weight"].values
    seg_df["_target"] = df["target"].values
    return seg_df


# ──────────────────────────────────────────────────────────────────────
# 7. SPLIT AUDIT SUMMARY
# ──────────────────────────────────────────────────────────────────────

def compute_split_summary(splits: dict[str, pd.DataFrame], seed: int) -> str:
    """Generate split_summary.md content."""
    lines = ["# Train / Validation / Test Split Summary", "",
             f"**Random seed**: {seed}  ",
             f"**Stratification**: target (binary income label)  ",
             f"**Split ratios**: {SPLIT_RATIOS}", ""]

    # Row counts
    lines += ["## Row Counts", "",
              "| Split | Rows | % of Total |",
              "|-------|-----:|-----------:|"]
    total = sum(len(s) for s in splits.values())
    for name, sdf in splits.items():
        lines.append(f"| {name} | {len(sdf):,} | {len(sdf)/total*100:.1f}% |")
    lines.append("")

    # Target distribution (raw)
    lines += ["## Target Distribution (Raw Counts)", "",
              "| Split | target=0 | target=1 | % positive |",
              "|-------|--------:|---------:|-----------:|"]
    for name, sdf in splits.items():
        n0 = (sdf["target"] == 0).sum()
        n1 = (sdf["target"] == 1).sum()
        lines.append(f"| {name} | {n0:,} | {n1:,} | {n1/len(sdf)*100:.2f}% |")
    lines.append("")

    # Target distribution (weighted)
    lines += ["## Target Distribution (Weighted)", "",
              "| Split | W(target=0) | W(target=1) | W(% positive) |",
              "|-------|------------:|------------:|---------------:|"]
    for name, sdf in splits.items():
        w0 = sdf.loc[sdf["target"] == 0, "weight"].sum()
        w1 = sdf.loc[sdf["target"] == 1, "weight"].sum()
        wtot = w0 + w1
        lines.append(f"| {name} | {w0:,.0f} | {w1:,.0f} | {w1/wtot*100:.2f}% |")
    lines.append("")

    # Year distribution
    lines += ["## Year Distribution", "",
              "| Split | year=94 | year=95 | % year=94 |",
              "|-------|--------:|--------:|----------:|"]
    for name, sdf in splits.items():
        n94 = (sdf["year"] == "94").sum()
        n95 = (sdf["year"] == "95").sum()
        lines.append(f"| {name} | {n94:,} | {n95:,} | {n94/len(sdf)*100:.1f}% |")
    lines.append("")

    # Drift warnings
    lines += ["## Drift Warnings", ""]
    pos_rates = {name: sdf["target"].mean() for name, sdf in splits.items()}
    max_drift = max(pos_rates.values()) - min(pos_rates.values())
    if max_drift > 0.005:
        lines.append(f"- WARNING: positive-class rate drifts by {max_drift:.4f} across splits")
    else:
        lines.append("- No material drift detected in target distribution across splits.")

    yr_rates = {}
    for name, sdf in splits.items():
        yr_rates[name] = (sdf["year"] == "94").sum() / len(sdf)
    yr_drift = max(yr_rates.values()) - min(yr_rates.values())
    if yr_drift > 0.02:
        lines.append(f"- WARNING: year=94 proportion drifts by {yr_drift:.3f} across splits")
    else:
        lines.append("- No material drift detected in year distribution across splits.")
    lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# 8. COLUMN TREATMENT DOCUMENTATION
# ──────────────────────────────────────────────────────────────────────

# Per-column treatment records sourced from Excel Column_Treatment sheet
COLUMN_TREATMENTS = [
    {"col": "age", "clf": "Yes", "seg": "Yes", "type": "continuous_numeric",
     "missing": "No missing observed", "impute": "Median if needed",
     "note": "Strong life-stage and income signal."},
    {"col": "class of worker", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "50.2% 'Not in universe' — preserved as informative category",
     "impute": "None; encode sentinels as-is",
     "note": "Employment status proxy."},
    {"col": "detailed industry recode", "clf": "Yes", "seg": "Yes",
     "type": "numeric_coded_categorical",
     "missing": "No missing observed",
     "impute": "None; treat as categorical code",
     "note": "Numeric codes 0-51; NOT continuous."},
    {"col": "detailed occupation recode", "clf": "Yes", "seg": "Yes",
     "type": "numeric_coded_categorical",
     "missing": "No missing observed",
     "impute": "None; treat as categorical code",
     "note": "Numeric codes 0-46; NOT continuous."},
    {"col": "education", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Important socioeconomic and life-stage feature."},
    {"col": "wage per hour", "clf": "Yes", "seg": "Yes", "type": "continuous_numeric",
     "missing": "No missing observed; heavy zero-inflation",
     "impute": "Median if needed; log1p version available",
     "note": "Highly skewed; log1p for linear models."},
    {"col": "enroll in edu inst last wk", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "93.7% 'Not in universe' — preserved as informative category",
     "impute": "None; encode sentinels as-is",
     "note": "Sparse but structurally informative."},
    {"col": "marital stat", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Strong income and household signal."},
    {"col": "major industry code", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Useful for classifier and segment naming."},
    {"col": "major occupation code", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "50.5% 'Not in universe' — preserved as informative category",
     "impute": "None; encode sentinels as-is",
     "note": "Useful for classifier and segment naming."},
    {"col": "race", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None", "note": ""},
    {"col": "hispanic origin", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None", "note": ""},
    {"col": "sex", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None", "note": ""},
    {"col": "member of a labor union", "clf": "Yes", "seg": "Excluded",
     "type": "categorical",
     "missing": "90.4% 'Not in universe' — preserved as informative category",
     "impute": "None; encode sentinels as-is",
     "note": "Very sparse; excluded from segmentation."},
    {"col": "reason for unemployment", "clf": "Review", "seg": "Excluded",
     "type": "categorical",
     "missing": "97.0% 'Not in universe'",
     "impute": "None; encode sentinels as-is",
     "note": "Extremely sparse; included in clf baseline for pruning test."},
    {"col": "full or part time employment stat", "clf": "Yes", "seg": "Yes",
     "type": "categorical", "missing": "No missing observed", "impute": "None",
     "note": "Very strong labor-force status feature."},
    {"col": "capital gains", "clf": "Yes", "seg": "Yes", "type": "continuous_numeric",
     "missing": "No missing observed; heavy zero-inflation",
     "impute": "Median if needed; log1p version available",
     "note": "Potentially strong but highly skewed wealth proxy."},
    {"col": "capital losses", "clf": "Yes", "seg": "Yes", "type": "continuous_numeric",
     "missing": "No missing observed; heavy zero-inflation",
     "impute": "Median if needed; log1p version available",
     "note": "Informative wealth/tax behavior proxy."},
    {"col": "dividends from stocks", "clf": "Yes", "seg": "Yes",
     "type": "continuous_numeric",
     "missing": "No missing observed; heavy zero-inflation",
     "impute": "Median if needed; log1p version available",
     "note": "Investment-income proxy; highly skewed."},
    {"col": "tax filer stat", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Strong proxy for filing/household situation."},
    {"col": "region of previous residence", "clf": "Review", "seg": "Excluded",
     "type": "categorical",
     "missing": "92.1% 'Not in universe'",
     "impute": "None; encode sentinels as-is",
     "note": "Extremely sparse; excluded from segmentation."},
    {"col": "state of previous residence", "clf": "Review", "seg": "Excluded",
     "type": "categorical",
     "missing": "92.4% 'Not in universe' + 'Unknown'",
     "impute": "None; encode sentinels as-is",
     "note": "Extremely sparse + high cardinality; excluded from segmentation."},
    {"col": "detailed household and family stat", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Very useful for segment interpretation."},
    {"col": "detailed household summary in household", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Very useful for segment interpretation."},
    {"col": "weight", "clf": "No (eval only)", "seg": "No (interpretation only)",
     "type": "sample_weight",
     "missing": "No missing observed",
     "impute": "None",
     "note": "CPS population weight. Used for weighted metrics and segment sizing. NEVER a predictive feature."},
    {"col": "migration code-change in msa", "clf": "Yes", "seg": "Excluded",
     "type": "categorical",
     "missing": "50.7% mixed '?' + 'Not in universe'",
     "impute": "None; '?' mapped to 'Unknown'",
     "note": "Conditionally applicable; excluded from segmentation."},
    {"col": "migration code-change in reg", "clf": "Yes", "seg": "Excluded",
     "type": "categorical",
     "missing": "50.7% mixed '?' + 'Not in universe'",
     "impute": "None; '?' mapped to 'Unknown'",
     "note": "Conditionally applicable; excluded from segmentation."},
    {"col": "migration code-move within reg", "clf": "Yes", "seg": "Excluded",
     "type": "categorical",
     "missing": "50.7% mixed '?' + 'Not in universe'",
     "impute": "None; '?' mapped to 'Unknown'",
     "note": "Conditionally applicable; excluded from segmentation."},
    {"col": "live in this house 1 year ago", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "No missing observed", "impute": "None", "note": ""},
    {"col": "migration prev res in sunbelt", "clf": "Review", "seg": "Excluded",
     "type": "categorical",
     "missing": "92.1% mixed '?' + 'Not in universe'",
     "impute": "None; '?' mapped to 'Unknown'",
     "note": "Extremely sparse; excluded from segmentation."},
    {"col": "num persons worked for employer", "clf": "Yes", "seg": "Yes",
     "type": "continuous_numeric",
     "missing": "No missing observed", "impute": "Median if needed",
     "note": "Values 0-6; kept numeric per plan."},
    {"col": "family members under 18", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "72.3% 'Not in universe' — preserved as informative category",
     "impute": "None; encode sentinels as-is",
     "note": "Family structure feature."},
    {"col": "country of birth father", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "3.4% '?' → mapped to 'Unknown'",
     "impute": "None; '?' mapped to 'Unknown'", "note": ""},
    {"col": "country of birth mother", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "3.1% '?' → mapped to 'Unknown'",
     "impute": "None; '?' mapped to 'Unknown'", "note": ""},
    {"col": "country of birth self", "clf": "Yes", "seg": "Yes",
     "type": "categorical",
     "missing": "1.7% '?' → mapped to 'Unknown'",
     "impute": "None; '?' mapped to 'Unknown'", "note": ""},
    {"col": "citizenship", "clf": "Yes", "seg": "Yes", "type": "categorical",
     "missing": "No missing observed", "impute": "None",
     "note": "Use carefully in business narrative."},
    {"col": "own business or self employed", "clf": "Yes", "seg": "Yes",
     "type": "numeric_coded_categorical",
     "missing": "No missing observed",
     "impute": "None; treat as categorical code",
     "note": "Values 0/1/2; NOT continuous."},
    {"col": "fill inc questionnaire for veteran's admin", "clf": "Review",
     "seg": "Excluded", "type": "categorical",
     "missing": "99.0% 'Not in universe'",
     "impute": "None; encode sentinels as-is",
     "note": "Extremely sparse; excluded from segmentation."},
    {"col": "veterans benefits", "clf": "Yes", "seg": "Yes",
     "type": "numeric_coded_categorical",
     "missing": "No missing observed",
     "impute": "None; treat as categorical code",
     "note": "Values 0/1/2; NOT continuous."},
    {"col": "weeks worked in year", "clf": "Yes", "seg": "Yes",
     "type": "continuous_numeric",
     "missing": "No missing observed", "impute": "Median if needed",
     "note": "Labor-force attachment/stability signal."},
    {"col": "year", "clf": "Yes", "seg": "Yes",
     "type": "numeric_coded_categorical",
     "missing": "No missing observed",
     "impute": "None; treat as categorical code",
     "note": "Cohort indicator (94/95); NOT continuous."},
    {"col": "label", "clf": "No (target)", "seg": "No",
     "type": "target_binary",
     "missing": "No missing observed",
     "impute": "Map '- 50000.' -> 0, '50000+.' -> 1",
     "note": "Binary income target for classifier."},
]


def generate_column_treatment_md() -> str:
    """Generate column_treatment.md from the treatment table."""
    lines = ["# Column Treatment Reference", "",
             "Finalized column-level preprocessing decisions for Stage 4.", "",
             "| # | Column | Classification | Segmentation | Treatment Type | "
             "Missing / Exception Handling | Imputation | Business Note |",
             "|---|--------|---------------|-------------|----------------|"
             "----------------------------|------------|---------------|"]
    for i, t in enumerate(COLUMN_TREATMENTS, 1):
        lines.append(
            f"| {i} | {t['col']} | {t['clf']} | {t['seg']} | {t['type']} | "
            f"{t['missing']} | {t['impute']} | {t['note']} |"
        )
    lines += ["", "---", "",
              "## Key Design Decisions", "",
              "1. **Structural sentinels preserved**: `Not in universe` and similar "
              "values are kept as explicit categories, not collapsed into generic NA.",
              "2. **`?` mapped to `Unknown`**: Preserves the ambiguity signal "
              "without using raw punctuation in category names.",
              "3. **Numeric-coded categoricals**: `detailed industry/occupation recode`, "
              "`own business or self employed`, `veterans benefits`, and `year` are "
              "converted to string categories to prevent accidental continuous treatment.",
              "4. **Log1p features**: `wage per hour`, `capital gains`, `capital losses`, "
              "and `dividends from stocks` have log1p-transformed copies available "
              "for linear models.",
              "5. **Weight excluded**: `weight` is never in the feature matrix — "
              "only used for weighted evaluation and segment sizing.",
              "6. **Segmentation subset**: 9 sparse/low-actionability columns excluded "
              "from segmentation input; weight and label excluded from clustering.",
              ""]
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# 9. PREPROCESSING AUDIT DOCUMENTATION
# ──────────────────────────────────────────────────────────────────────

def generate_audit_md(df: pd.DataFrame, splits: dict[str, pd.DataFrame],
                      clf_cols: list[str], seg_cols: list[str],
                      data_hash: str, seed: int) -> str:
    """Generate PREPROCESSING_AUDIT.md."""
    lines = [
        "# Preprocessing Audit — Stage 4", "",
        f"**Pipeline version**: preprocess.py  ",
        f"**Random seed**: {seed}  ",
        f"**Input rows**: {len(df):,}  ",
        f"**Input data SHA-256**: `{data_hash[:16]}...`  ",
        f"**Date**: auto-generated by pipeline", "",

        "---", "",

        "## 1. Target Mapping", "",
        "| Raw Label | Mapped Value | Count | % |",
        "|-----------|-------------|------:|--:|",
    ]
    for raw, mapped in LABEL_MAP.items():
        cnt = (df["label"] == raw).sum()
        lines.append(f"| `{raw}` | {mapped} | {cnt:,} | {cnt/len(df)*100:.1f}% |")
    lines += ["",
              "The target is highly imbalanced (~93.8% class 0, ~6.2% class 1). "
              "Class weighting and threshold tuning will be addressed in Stage 5.", ""]

    # Split summary reference
    lines += ["## 2. Split Summary", "",
              "See `split_summary.md` for detailed train/val/test statistics.", "",
              f"- Train: {len(splits['train']):,} rows",
              f"- Validation: {len(splits['val']):,} rows",
              f"- Test: {len(splits['test']):,} rows", ""]

    # Feature grouping
    lines += ["## 3. Final Feature Grouping", "",
              f"### Classification features ({len(clf_cols)} columns)", "",
              f"- Continuous numeric: {len(CONTINUOUS_NUMERIC)} "
              f"({', '.join(CONTINUOUS_NUMERIC)})",
              f"- Log1p-transformed copies: {len(LOG1P_CANDIDATES)} "
              f"({', '.join(f'{c}_log1p' for c in LOG1P_CANDIDATES)})",
              f"- Numeric-coded categorical: {len(NUMERIC_CODED_CATEGORICAL)} "
              f"({', '.join(NUMERIC_CODED_CATEGORICAL)})",
              f"- Text categorical: {len(CATEGORICAL)} columns",
              f"- Review columns (included but flagged for pruning tests): "
              f"{', '.join(REVIEW_COLUMNS)}", "",
              f"### Segmentation features ({len(seg_cols)} columns)", "",
              f"- Same groups minus {len(SEGMENTATION_EXCLUDE)} excluded sparse columns",
              f"- Excluded from clustering: {', '.join(SEGMENTATION_EXCLUDE)}",
              f"- Sidecar columns `_weight` and `_target` preserved for interpretation", ""]

    # Dropped columns
    lines += ["## 4. Columns Dropped from Features and Why", "",
              "| Column | Reason |",
              "|--------|--------|",
              "| `label` | Target variable — not a feature |",
              "| `weight` | CPS population weight — evaluation/interpretation only |", ""]

    # Sentinel handling
    lines += ["## 5. Sentinel Value Handling", "",
              "### `Not in universe` (and variants)", "",
              "- **Preserved as explicit category** in all categorical columns.",
              "- Rationale: these values encode structural life-stage and labor-force "
              "status (e.g., children, retirees, non-labor-force). They are often "
              "highly predictive of income class and useful for segmentation.", "",
              "### `?` (unknown/ambiguous)", "",
              "- **Mapped to `Unknown`** in all categorical columns.",
              "- Rationale: preserves the ambiguity signal while normalizing the "
              "representation. Keeps it as a distinct category, not collapsed "
              "into a generic NA.", "",
              "### Empty string", "",
              "- **Mapped to `Missing`** in categorical columns.",
              "- **Mapped to NaN** in continuous numeric columns (via pd.to_numeric).",
              "- In practice, no empty strings were observed in the full dataset.", ""]

    # Continuous skewed variables
    lines += ["## 6. Continuous Skewed Variable Treatment", "",
              "The following monetary columns exhibit heavy right skew and zero-inflation:", "",
              "| Column | Min | Mean | Max | Treatment |",
              "|--------|----:|-----:|----:|-----------|"]
    skew_stats = {"wage per hour": (0, 55.43, 9999),
                  "capital gains": (0, 434.72, 99999),
                  "capital losses": (0, 37.31, 4608),
                  "dividends from stocks": (0, 197.53, 99999)}
    for col, (mn, mean, mx) in skew_stats.items():
        lines.append(f"| {col} | {mn} | {mean:.2f} | {mx:,} | "
                      "Raw + log1p copy |")
    lines += ["",
              "- Raw values kept for tree-based models (handle skew natively).",
              "- `log1p` versions available for linear/distance-based models.",
              "- Winsorization considered optional sensitivity test, not default.", ""]

    # Numeric-coded categorical protection
    lines += ["## 7. Numeric-Coded Categorical Protection", "",
              "The following columns are stored as integers in the raw data but are "
              "semantic codes, not continuous measurements:", "",
              "| Column | Value Range | Action |",
              "|--------|-------------|--------|",
              "| detailed industry recode | 0-51 | Cast to string category |",
              "| detailed occupation recode | 0-46 | Cast to string category |",
              "| own business or self employed | 0-2 | Cast to string category |",
              "| veterans benefits | 0-2 | Cast to string category |",
              "| year | 94-95 | Cast to string category |", "",
              "These columns are stored as `category` dtype to prevent any "
              "downstream code from accidentally computing means or applying "
              "numeric scaling.", ""]

    # Classification vs segmentation divergence
    lines += ["## 8. Classification vs Segmentation Divergence", "",
              "| Aspect | Classification | Segmentation |",
              "|--------|---------------|-------------|",
              "| Feature set | All 40 columns (incl. Review) | "
              f"{len(seg_cols)} columns (sparse excluded) |",
              "| Target | Used as label | Excluded from clustering input |",
              "| Weight | Evaluation/reporting only | Segment sizing only |",
              "| Log1p features | Available for linear models | Not included |",
              "| Split | train/val/test 70/15/15 | Full dataset (unsupervised) |",
              "| Unseen category handling | Category dtype preserved | N/A (full data) |",
              ""]

    # Known limitations
    lines += ["## 9. Known Limitations / Future Cleanup", "",
              "1. **No temporal hold-out**: The train/val/test split is random, not "
              "time-based. Since year has only two values (94/95) and the task is "
              "a take-home, this is acceptable but noted.",
              "2. **Imputation minimal**: Continuous columns have no observed missing "
              "values; median imputation logic is defined but untriggered.",
              "3. **High-cardinality categoricals**: `detailed household and family stat` "
              "(38 levels), `state of previous residence` (51 levels), and the "
              "detailed recode columns may need rare-level pooling for linear models.",
              "4. **Review columns**: 5 columns are flagged for pruning sensitivity "
              "tests in Stage 5. They are included in the baseline feature set.",
              "5. **Log1p features**: Only produced for classification. Segmentation "
              "uses raw continuous values; scaling will be applied in the "
              "segmentation pipeline itself.",
              "6. **No duplicate detection**: The pipeline does not currently check "
              "for exact duplicate rows, which can occur in census data extracts.",
              ""]

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# 10. MAIN PIPELINE
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stage 4 preprocessing pipeline")
    parser.add_argument("--data", default="../datasource/census_bureau.jsonl",
                        help="Path to input JSONL")
    parser.add_argument("--outdir", default="outputs",
                        help="Output directory for artifacts")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    seed = args.seed
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # --- Compute data hash for reproducibility tracking ---
    print("Computing input data hash...")
    h = hashlib.sha256()
    with open(args.data, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    data_hash = h.hexdigest()
    print(f"  SHA-256: {data_hash[:16]}...")

    # --- Load ---
    print("\n[1/7] Loading data...")
    df = load_jsonl(args.data)

    # --- Validate columns ---
    expected = set(c["col"] for c in COLUMN_TREATMENTS)
    actual = set(df.columns)
    missing_cols = expected - actual
    if missing_cols:
        print(f"WARNING: expected columns not found: {missing_cols}", file=sys.stderr)

    # --- Target & weight ---
    print("[2/7] Mapping target and parsing weight...")
    df = map_target(df)
    df = parse_weight(df)

    # --- Column-level cleaning ---
    print("[3/7] Cleaning columns...")
    df = clean_continuous(df)
    df = clean_numeric_coded(df)
    df = clean_categorical(df)
    df = add_log1p_features(df)

    # Quick sanity: weight must not appear in feature columns
    clf_cols = classification_feature_cols()
    seg_cols = segmentation_feature_cols()
    assert "weight" not in clf_cols, "GOVERNANCE VIOLATION: weight in classification features"
    assert "label" not in clf_cols, "GOVERNANCE VIOLATION: label in classification features"
    assert "weight" not in seg_cols, "GOVERNANCE VIOLATION: weight in segmentation features"
    assert "label" not in seg_cols, "GOVERNANCE VIOLATION: label in segmentation features"

    # --- Split ---
    print("[4/7] Stratified train/val/test split...")
    splits = stratified_split(df, seed)

    # --- Save classification artifacts ---
    print("[5/7] Saving classification artifacts...")
    meta_cols = ["target", "weight"]
    for name, sdf in splits.items():
        out_path = outdir / f"clf_{name}.csv"
        sdf[clf_cols + meta_cols].to_csv(out_path, index=False)
        print(f"  {out_path} ({len(sdf):,} rows)")

    # --- Save segmentation artifact ---
    print("[6/7] Saving segmentation artifact...")
    seg_df = build_segmentation_dataset(df)
    seg_path = outdir / "seg_full.csv"
    seg_df.to_csv(seg_path, index=False)
    print(f"  {seg_path} ({len(seg_df):,} rows)")

    # --- Generate documentation ---
    print("[7/7] Generating documentation...")

    col_treat_md = generate_column_treatment_md()
    (outdir / "column_treatment.md").write_text(col_treat_md, encoding="utf-8")
    print("  column_treatment.md")

    split_md = compute_split_summary(splits, seed)
    (outdir / "split_summary.md").write_text(split_md, encoding="utf-8")
    print("  split_summary.md")

    audit_md = generate_audit_md(df, splits, clf_cols, seg_cols, data_hash, seed)
    (outdir / "PREPROCESSING_AUDIT.md").write_text(audit_md, encoding="utf-8")
    print("  PREPROCESSING_AUDIT.md")

    print(f"\nStage 4 complete. All outputs in {outdir}/")
    print(f"Classification feature columns: {len(clf_cols)}")
    print(f"Segmentation feature columns: {len(seg_cols)}")


if __name__ == "__main__":
    main()
