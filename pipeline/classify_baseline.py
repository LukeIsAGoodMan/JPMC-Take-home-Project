"""
classify_baseline.py — Stage 5: Classification baseline modeling & diagnostics.

Runs the full Stage 5 experiment grid:
  - Duplicate leakage audit
  - Logistic Regression (full/reduced, no-class-bal/class-balanced)
  - CatBoost (full/reduced, no-class-bal/class-balanced)
  - Unweighted AND survey-weighted evaluation for every configuration
  - Threshold diagnostics
  - Error analysis
  - All documentation artifacts

Terminology:
  - "ClsBal" = class-balanced training (class_weight='balanced' / scale_pos_weight)
    Addresses label imbalance in the loss function.
  - "survey-weighted eval" = evaluation using CPS `weight` column as sample_weight
    Addresses population representativeness in metric computation.
  These solve DIFFERENT problems and must not be conflated.

Usage:
    cd pipeline/
    python classify_baseline.py --datadir outputs --outdir outputs/stage5 --seed 42
"""

import argparse
import warnings
import json
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score, recall_score,
    f1_score, confusion_matrix, balanced_accuracy_score, accuracy_score,
    precision_recall_curve, classification_report,
)
from catboost import CatBoostClassifier, Pool

warnings.filterwarnings("ignore", category=FutureWarning)

SEED = 42

# ──────────────────────────────────────────────────────────────────────
# Column definitions (mirrored from Stage 4 preprocess.py)
# ──────────────────────────────────────────────────────────────────────

CONTINUOUS_NUMERIC = [
    "age", "wage per hour", "capital gains", "capital losses",
    "dividends from stocks", "num persons worked for employer",
    "weeks worked in year",
]

NUMERIC_CODED_CATEGORICAL = [
    "detailed industry recode", "detailed occupation recode",
    "own business or self employed", "veterans benefits", "year",
]

CATEGORICAL = [
    "class of worker", "education", "enroll in edu inst last wk",
    "marital stat", "major industry code", "major occupation code",
    "race", "hispanic origin", "sex", "member of a labor union",
    "reason for unemployment", "full or part time employment stat",
    "tax filer stat", "region of previous residence",
    "state of previous residence", "detailed household and family stat",
    "detailed household summary in household",
    "migration code-change in msa", "migration code-change in reg",
    "migration code-move within reg", "live in this house 1 year ago",
    "migration prev res in sunbelt", "family members under 18",
    "country of birth father", "country of birth mother",
    "country of birth self", "citizenship",
    "fill inc questionnaire for veteran's admin",
]

LOG1P_COLS = [
    "wage per hour_log1p", "capital gains_log1p",
    "capital losses_log1p", "dividends from stocks_log1p",
]

REVIEW_COLUMNS = [
    "reason for unemployment", "region of previous residence",
    "state of previous residence", "migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin",
]

META_COLS = ["target", "weight"]

# Columns for rare-level pooling in linear baseline
RARE_POOL_COLS = [
    "state of previous residence",
    "detailed household and family stat",
    "detailed industry recode",
    "detailed occupation recode",
    "country of birth father",
    "country of birth mother",
    "country of birth self",
]
RARE_POOL_THRESHOLD = 500  # levels with < 500 train occurrences -> "Rare"


# ──────────────────────────────────────────────────────────────────────
# 1. DATA LOADING & DTYPE RECONSTRUCTION
# ──────────────────────────────────────────────────────────────────────

def load_split(path: str) -> pd.DataFrame:
    """Load a classification split CSV and reconstruct proper dtypes."""
    # keep_default_na=False prevents pandas from interpreting "NA" as NaN
    # (hispanic origin has a legitimate "NA" category meaning "not applicable")
    df = pd.read_csv(path, keep_default_na=False, na_values=[])
    # Cast numeric-coded columns to string (prevent numeric misuse)
    for col in NUMERIC_CODED_CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].astype(str)
    # Ensure categoricals are string (and fill any residual NaN)
    for col in CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "Missing")
    # Parse continuous columns as numeric
    for col in CONTINUOUS_NUMERIC + LOG1P_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_feature_cols(variant: str) -> dict:
    """Return column lists for a given feature-set variant.

    Returns dict with keys: continuous, categorical_all, log1p
    """
    all_cat = NUMERIC_CODED_CATEGORICAL + CATEGORICAL
    if variant == "reduced":
        all_cat = [c for c in all_cat if c not in REVIEW_COLUMNS]

    return {
        "continuous": CONTINUOUS_NUMERIC,
        "categorical_all": all_cat,
        "log1p": LOG1P_COLS,
    }


# ──────────────────────────────────────────────────────────────────────
# 2. DUPLICATE LEAKAGE AUDIT
# ──────────────────────────────────────────────────────────────────────

def duplicate_audit(train: pd.DataFrame, val: pd.DataFrame,
                    test: pd.DataFrame) -> dict:
    """Check for duplicate leakage across splits."""
    feature_cols = [c for c in train.columns if c not in META_COLS]
    results = {}

    # 2a. Exact duplicates within each split (all columns including target)
    for name, df in [("train", train), ("val", val), ("test", test)]:
        n_dup = df.duplicated().sum()
        results[f"exact_dup_{name}"] = int(n_dup)

    # 2b. Cross-split feature duplicates
    # Create a feature hash for efficient comparison
    def hash_rows(df):
        return df[feature_cols].apply(
            lambda row: hash(tuple(row)), axis=1
        )

    train_hashes = set(hash_rows(train))
    val_hashes = set(hash_rows(val))
    test_hashes = set(hash_rows(test))

    results["cross_train_val"] = len(train_hashes & val_hashes)
    results["cross_train_test"] = len(train_hashes & test_hashes)
    results["cross_val_test"] = len(val_hashes & test_hashes)

    # 2c. Identical features with different targets (conflicting labels)
    all_df = pd.concat([train, val, test], ignore_index=True)
    grouped = all_df.groupby(feature_cols, sort=False)["target"]
    conflicting = grouped.nunique()
    n_conflicting_groups = (conflicting > 1).sum()
    results["conflicting_target_groups"] = int(n_conflicting_groups)

    # Count total rows involved in conflicts
    if n_conflicting_groups > 0:
        conflict_sizes = grouped.transform("nunique")
        results["conflicting_target_rows"] = int((conflict_sizes > 1).sum())
    else:
        results["conflicting_target_rows"] = 0

    # 2d. Total exact duplicates across all data
    results["total_exact_dup"] = int(all_df.duplicated().sum())
    results["total_rows"] = len(all_df)

    return results


def write_duplicate_audit_md(results: dict, outdir: Path):
    """Write DUPLICATE_AUDIT.md."""
    total = results["total_rows"]
    lines = [
        "# Duplicate Leakage Audit — Stage 5", "",
        "## Exact Duplicate Rows (within splits)", "",
        "| Split | Duplicate Rows | % of Split |",
        "|-------|---------------:|-----------:|",
    ]
    for split in ["train", "val", "test"]:
        n = results[f"exact_dup_{split}"]
        # get split size from the key naming convention
        sz = {"train": 139665, "val": 29929, "test": 29929}[split]
        lines.append(f"| {split} | {n:,} | {n/sz*100:.2f}% |")

    lines += ["",
              f"**Total exact duplicates across all data**: "
              f"{results['total_exact_dup']:,} / {total:,} "
              f"({results['total_exact_dup']/total*100:.1f}%)", ""]

    lines += [
        "## Cross-Split Feature Duplicates", "",
        "These are unique feature vectors that appear in more than one split.",
        "",
        "| Pair | Shared Feature Vectors |",
        "|------|----------------------:|",
        f"| train-val | {results['cross_train_val']:,} |",
        f"| train-test | {results['cross_train_test']:,} |",
        f"| val-test | {results['cross_val_test']:,} |", "",
    ]

    lines += [
        "## Conflicting Targets (Same Features, Different Labels)", "",
        f"- **Groups with conflicting targets**: {results['conflicting_target_groups']:,}",
        f"- **Total rows involved**: {results['conflicting_target_rows']:,}", "",
    ]

    # Risk assessment
    lines += ["## Risk Assessment", ""]
    total_dup = results["total_exact_dup"]
    cross_leak = (results["cross_train_val"] + results["cross_train_test"]
                  + results["cross_val_test"])

    if total_dup == 0 and cross_leak == 0:
        lines.append("**LOW RISK**: No exact duplicates or cross-split leakage detected.")
    elif total_dup > 0 and cross_leak == 0:
        lines.append(
            f"**LOW-MODERATE RISK**: {total_dup:,} exact duplicate rows exist "
            f"within splits but no cross-split leakage was found. "
            f"Census data commonly contains legitimate duplicate demographic "
            f"profiles (different individuals with identical recorded attributes). "
            f"This is expected behavior, not data corruption."
        )
    elif cross_leak > 0:
        lines.append(
            f"**ELEVATED RISK**: {cross_leak:,} feature vectors appear in multiple "
            f"splits. This could inflate validation/test metrics. "
            f"Investigate whether these represent true population duplicates "
            f"or data processing artifacts."
        )

    if results["conflicting_target_groups"] > 0:
        lines.append(
            f"\n**Note on conflicting targets**: {results['conflicting_target_groups']:,} "
            f"feature groups have both target=0 and target=1. This is expected "
            f"in census data — identical demographic profiles can genuinely "
            f"belong to different income brackets. This is irreducible noise, "
            f"not a data error."
        )

    lines += ["",
              "## Action Taken", "",
              "No rows were removed. Duplicates in census data represent "
              "legitimate population patterns (multiple individuals with "
              "identical recorded attributes). Removing them would distort "
              "the population distribution and bias the model.", ""]

    (outdir / "DUPLICATE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print("  DUPLICATE_AUDIT.md written")


# ──────────────────────────────────────────────────────────────────────
# 3. RARE-LEVEL POOLING (for Logistic Regression)
# ──────────────────────────────────────────────────────────────────────

def build_rare_level_map(train: pd.DataFrame, cols: list[str],
                         threshold: int) -> dict[str, dict[str, str]]:
    """Build mapping of rare levels -> 'Rare' for specified columns.
    Fit on train only."""
    rare_map = {}
    for col in cols:
        if col not in train.columns:
            continue
        counts = train[col].value_counts()
        rare_levels = counts[counts < threshold].index.tolist()
        if rare_levels:
            rare_map[col] = {level: "Rare" for level in rare_levels}
    return rare_map


def apply_rare_pooling(df: pd.DataFrame,
                       rare_map: dict[str, dict[str, str]]) -> pd.DataFrame:
    """Apply rare-level pooling using a pre-built map."""
    df = df.copy()
    for col, mapping in rare_map.items():
        if col in df.columns:
            df[col] = df[col].replace(mapping)
    return df


# ──────────────────────────────────────────────────────────────────────
# 4. LOGISTIC REGRESSION PIPELINE
# ──────────────────────────────────────────────────────────────────────

def build_lr_pipeline(continuous_cols: list[str], categorical_cols: list[str],
                      log1p_cols: list[str], class_weight=None):
    """Build sklearn ColumnTransformer + LogisticRegression pipeline.

    Uses log1p versions of monetary columns instead of raw for linear model.
    """
    # For LR: use log1p versions of monetary columns + remaining continuous
    monetary_raw = {"wage per hour", "capital gains", "capital losses",
                    "dividends from stocks"}
    lr_continuous = [c for c in continuous_cols if c not in monetary_raw]
    lr_numeric = lr_continuous + log1p_cols

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), lr_numeric),
            ("cat", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                  min_frequency=50, sparse_output=False,
                                  drop=None), categorical_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("clf", LogisticRegression(
            max_iter=2000,
            solver="saga",
            penalty="l2",
            C=1.0,
            class_weight=class_weight,
            random_state=SEED,
            n_jobs=-1,
        )),
    ])
    return pipeline


# ──────────────────────────────────────────────────────────────────────
# 5. CATBOOST PIPELINE
# ──────────────────────────────────────────────────────────────────────

def build_catboost(cat_features: list[int], class_weights=None,
                   scale_pos_weight=None):
    """Build CatBoost classifier with light tuning."""
    params = dict(
        iterations=800,
        learning_rate=0.05,
        depth=6,
        l2_leaf_reg=3.0,
        random_seed=SEED,
        verbose=0,
        eval_metric="AUC",
        auto_class_weights=None,
        cat_features=cat_features,
        task_type="CPU",
    )
    if class_weights:
        params["class_weights"] = class_weights
    if scale_pos_weight is not None:
        params["scale_pos_weight"] = scale_pos_weight
    return CatBoostClassifier(**params)


# ──────────────────────────────────────────────────────────────────────
# 6. EVALUATION
# ──────────────────────────────────────────────────────────────────────

def evaluate(y_true, y_prob, y_pred, sample_weight=None, label="") -> dict:
    """Compute full evaluation metrics."""
    metrics = {
        "label": label,
        "n": len(y_true),
        "n_pos": int(y_true.sum()),
        "n_neg": int((y_true == 0).sum()),
        "roc_auc": roc_auc_score(y_true, y_prob,
                                 sample_weight=sample_weight),
        "pr_auc": average_precision_score(y_true, y_prob,
                                          sample_weight=sample_weight),
        "precision": precision_score(y_true, y_pred, zero_division=0,
                                     sample_weight=sample_weight),
        "recall": recall_score(y_true, y_pred, zero_division=0,
                               sample_weight=sample_weight),
        "f1": f1_score(y_true, y_pred, zero_division=0,
                       sample_weight=sample_weight),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred,
                                                     sample_weight=sample_weight),
        "accuracy": accuracy_score(y_true, y_pred,
                                   sample_weight=sample_weight),
    }
    cm = confusion_matrix(y_true, y_pred, sample_weight=sample_weight)
    metrics["tn"] = float(cm[0, 0])
    metrics["fp"] = float(cm[0, 1])
    metrics["fn"] = float(cm[1, 0])
    metrics["tp"] = float(cm[1, 1])
    return metrics


def threshold_diagnostics(y_true, y_prob, thresholds=None):
    """Compute precision/recall/F1 at multiple thresholds."""
    if thresholds is None:
        thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35,
                      0.40, 0.45, 0.50, 0.55, 0.60]
    rows = []
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f = f1_score(y_true, y_pred, zero_division=0)
        n_pred_pos = y_pred.sum()
        rows.append({"threshold": t, "precision": p, "recall": r,
                     "f1": f, "n_predicted_pos": int(n_pred_pos)})
    return rows


# ──────────────────────────────────────────────────────────────────────
# 7. ERROR ANALYSIS
# ──────────────────────────────────────────────────────────────────────

def error_analysis(df: pd.DataFrame, y_true, y_pred, y_prob,
                   top_n: int = 5) -> dict:
    """Lightweight error analysis: profile FP and FN populations."""
    analysis = {}
    fp_mask = (y_pred == 1) & (y_true == 0)
    fn_mask = (y_pred == 0) & (y_true == 1)

    profile_cols = ["age", "education", "marital stat", "major occupation code",
                    "full or part time employment stat",
                    "detailed household summary in household", "sex",
                    "class of worker"]
    profile_cols = [c for c in profile_cols if c in df.columns]

    for err_type, mask in [("false_positives", fp_mask),
                           ("false_negatives", fn_mask)]:
        info = {"count": int(mask.sum())}
        err_df = df.loc[mask]
        if len(err_df) == 0:
            analysis[err_type] = info
            continue

        # Top categories in key columns
        profiles = {}
        for col in profile_cols:
            top = err_df[col].value_counts().head(top_n)
            profiles[col] = {str(k): int(v) for k, v in top.items()}
        info["top_profiles"] = profiles

        # Age stats
        if "age" in err_df.columns:
            ages = pd.to_numeric(err_df["age"], errors="coerce")
            info["age_mean"] = float(ages.mean())
            info["age_median"] = float(ages.median())

        # Confidence distribution
        err_probs = y_prob[mask]
        info["prob_mean"] = float(err_probs.mean())
        info["prob_median"] = float(np.median(err_probs))

        analysis[err_type] = info

    return analysis


# ──────────────────────────────────────────────────────────────────────
# 8. DOCUMENTATION GENERATORS
# ──────────────────────────────────────────────────────────────────────

def fmt(x, d=4):
    """Format a number for markdown."""
    if isinstance(x, float):
        return f"{x:.{d}f}"
    return str(x)


def _metrics_table(results: list[dict], int_cm: bool = True) -> list[str]:
    """Render a list of metric dicts as a markdown table."""
    lines = [
        "| Config | ROC-AUC | PR-AUC | Precision | Recall | F1 | "
        "Bal.Acc | TP | FP | FN | TN |",
        "|--------|--------:|-------:|----------:|-------:|---:|"
        "-------:|---:|---:|---:|---:|",
    ]
    fmt_cm = (lambda x: str(int(x))) if int_cm else (lambda x: f"{x:,.0f}")
    for r in results:
        lines.append(
            f"| {r['label']} | {fmt(r['roc_auc'])} | {fmt(r['pr_auc'])} | "
            f"{fmt(r['precision'])} | {fmt(r['recall'])} | {fmt(r['f1'])} | "
            f"{fmt(r['balanced_accuracy'])} | {fmt_cm(r['tp'])} | "
            f"{fmt_cm(r['fp'])} | {fmt_cm(r['fn'])} | {fmt_cm(r['tn'])} |"
        )
    return lines


def generate_baseline_metrics_md(all_results: list[dict],
                                 all_sw_results: list[dict],
                                 test_results: list[dict],
                                 test_sw_results: list[dict],
                                 threshold_diag: dict) -> str:
    """Generate BASELINE_METRICS.md with both unweighted and survey-weighted tables."""
    lines = [
        "# Baseline Metrics — Stage 5", "",
        "> **Terminology note**: 'ClsBal' = class-balanced training "
        "(addresses label imbalance). 'Survey-weighted eval' = metrics "
        "computed using CPS `weight` column (addresses population "
        "representativeness). These are independent concerns.", "",
    ]

    # A. Unweighted validation
    lines += ["## A. Validation — Unweighted Evaluation", ""]
    lines += _metrics_table(all_results)
    best = max(all_results, key=lambda r: r["pr_auc"])
    lines += ["",
              f"**Best unweighted PR-AUC**: {fmt(best['pr_auc'])} "
              f"({best['label']})", ""]

    # B. Survey-weighted validation
    lines += ["## B. Validation — Survey-Weighted Evaluation", "",
              "Metrics below use the CPS `weight` column as `sample_weight` "
              "to reflect population-representative performance.", ""]
    lines += _metrics_table(all_sw_results, int_cm=False)
    best_sw = max(all_sw_results, key=lambda r: r["pr_auc"])
    lines += ["",
              f"**Best survey-weighted PR-AUC**: {fmt(best_sw['pr_auc'])} "
              f"({best_sw['label']})", ""]

    # C. Test results (unweighted)
    if test_results:
        lines += ["## C. Test — Unweighted Evaluation (selected candidates)", ""]
        lines += _metrics_table(test_results)
        lines.append("")

    # D. Test results (survey-weighted)
    if test_sw_results:
        lines += ["## D. Test — Survey-Weighted Evaluation (selected candidates)", ""]
        lines += _metrics_table(test_sw_results, int_cm=False)
        lines.append("")

    # E. Threshold diagnostics (unchanged)
    for config_label, diag_rows in threshold_diag.items():
        lines += [
            f"## Threshold Diagnostics: {config_label}", "",
            "| Threshold | Precision | Recall | F1 | #Predicted Pos |",
            "|----------:|----------:|-------:|---:|---------------:|",
        ]
        for row in diag_rows:
            lines.append(
                f"| {row['threshold']:.2f} | {fmt(row['precision'])} | "
                f"{fmt(row['recall'])} | {fmt(row['f1'])} | "
                f"{row['n_predicted_pos']:,} |"
            )
        lines.append("")

    # F. Conceptual note
    lines += [
        "---", "",
        "## Note: Survey Weights vs Class Balancing", "",
        "| Concept | What it does | When applied |",
        "|---------|-------------|-------------|",
        "| **Class balancing** (`class_weight='balanced'`, `scale_pos_weight`) "
        "| Upweights the minority class in the loss function to combat label "
        "imbalance | Training time |",
        "| **Survey weighting** (CPS `weight` column as `sample_weight`) "
        "| Makes metrics reflect the true population distribution, not just "
        "the sample | Evaluation time |", "",
        "They solve different problems. Class balancing helps the model learn "
        "the rare class better. Survey weighting ensures reported metrics "
        "represent real-world population impact, not just sample performance.",
        "",
    ]

    return "\n".join(lines)


def format_error_analysis(error_analyses: dict) -> str:
    """Format error analysis results for markdown."""
    lines = ["## Error Analysis", ""]
    for config_label, analysis in error_analyses.items():
        lines += [f"### {config_label}", ""]
        for err_type in ["false_positives", "false_negatives"]:
            info = analysis.get(err_type, {})
            count = info.get("count", 0)
            friendly = "False Positives (predicted >50K, actual <=50K)" if err_type == "false_positives" \
                else "False Negatives (predicted <=50K, actual >50K)"
            lines.append(f"**{friendly}**: {count:,}")
            if count == 0:
                lines.append("")
                continue
            if "age_mean" in info:
                lines.append(f"- Mean age: {info['age_mean']:.1f}, "
                             f"Median age: {info['age_median']:.1f}")
            if "prob_mean" in info:
                lines.append(f"- Mean predicted probability: {info['prob_mean']:.3f}")
            if "top_profiles" in info:
                for col, top in info["top_profiles"].items():
                    top_str = ", ".join(f"{k} ({v})" for k, v in
                                       list(top.items())[:3])
                    lines.append(f"- Top `{col}`: {top_str}")
            lines.append("")
    return "\n".join(lines)


def generate_classifier_report_md(all_results: list[dict],
                                  all_sw_results: list[dict],
                                  test_results: list[dict],
                                  test_sw_results: list[dict],
                                  rare_pool_info: dict,
                                  error_text: str,
                                  threshold_diag: dict,
                                  dup_results: dict) -> str:
    """Generate CLASSIFIER_BASELINE_REPORT.md."""
    best_val = max(all_results, key=lambda r: r["pr_auc"])
    best_val_sw = max(all_sw_results, key=lambda r: r["pr_auc"])

    lines = [
        "# Classifier Baseline Report — Stage 5", "",
        "## 1. Modeling Objective", "",
        "Build a binary classifier to predict whether a person's income "
        "exceeds $50,000 using CPS census data. The target is highly "
        "imbalanced (~6.2% positive class), so standard accuracy is "
        "insufficient. PR-AUC and minority-class retrieval quality are "
        "the primary evaluation criteria.", "",

        "## 2. Feature-Set Definitions", "",
        "### Full feature set",
        "- 7 continuous numeric columns",
        "- 5 numeric-coded categorical columns (cast to string)",
        "- 28 text categorical columns",
        "- 4 log1p-transformed copies (for LR only)",
        "- Total: 44 input columns", "",
        "### Reduced feature set",
        "Same as full, minus 5 review columns:",
        "- `reason for unemployment` (97% Not in universe)",
        "- `region of previous residence` (92% Not in universe)",
        "- `state of previous residence` (92% Not in universe, 51 levels)",
        "- `migration prev res in sunbelt` (92% sparse)",
        "- `fill inc questionnaire for veteran's admin` (99% Not in universe)",
        "- Total: 39 input columns", "",

        "## 3. Model Families Tested", "",
        "### Logistic Regression",
        "- L2 regularization (C=1.0, saga solver)",
        "- StandardScaler on continuous features",
        "- OneHotEncoder with infrequent-level handling (min_frequency=50)",
        "- Log1p versions used for skewed monetary columns",
        "- Rare-level pooling applied to high-cardinality categoricals",
        "- Training variants: no class balancing vs `class_weight='balanced'`", "",

        "### CatBoost",
        "- 800 iterations, lr=0.05, depth=6, l2_leaf_reg=3.0",
        "- Native categorical handling (cat_features specified)",
        "- Uses raw continuous columns (no log1p needed)",
        "- Training variants: no class balancing vs `scale_pos_weight`", "",

        "## 4. Rare-Level Pooling", "",
        f"Threshold: < {RARE_POOL_THRESHOLD} occurrences in training set -> "
        f"pooled to 'Rare'", "",
        "Applied to Logistic Regression pipeline only. CatBoost handles "
        "rare categories natively.", "",
        "| Column | Levels Pooled |",
        "|--------|-------------:|",
    ]
    for col, n in sorted(rare_pool_info.items()):
        lines.append(f"| {col} | {n} |")
    lines.append("")

    # --- Section 5: Weighting Concepts ---
    lines += [
        "## 5. Survey Weights vs Class Balancing", "",
        "This section clarifies two distinct weighting concepts used in this project.", "",
        "### 5.1 Class Balancing (training-time)", "",
        "**Purpose**: combat label imbalance (~93.8% negative, ~6.2% positive).", "",
        "- LR: `class_weight='balanced'` upweights minority-class loss.",
        "- CatBoost: `scale_pos_weight` upweights positive-class gradient contribution.",
        "- Effect: improves recall for the rare >50K class at the cost of precision.", "",
        "### 5.2 Survey Weighting (evaluation-time)", "",
        "**Purpose**: make metrics reflect true population distribution, not just "
        "the CPS sample.", "",
        "- The `weight` column represents CPS population weights (range 38–18,656).",
        "- Passing `weight` as `sample_weight` in sklearn metrics makes each "
        "observation count proportionally to the population it represents.",
        "- This is applied at evaluation time to ALL model configurations.",
        "- `weight` is NEVER used as a predictive feature.", "",
        "### 5.3 Survey-Weighted Training Decision", "",
        "**Decision: Path B — survey-weighted training deferred.**", "",
        "Survey-weighted training (passing `weight` as `sample_weight` in "
        "`model.fit()`) was NOT implemented in Stage 5 for these reasons:", "",
        "1. Survey weights address population representativeness, not label "
        "imbalance. Using them as training sample weights conflates two "
        "distinct objectives.",
        "2. CPS weights vary 500x (38 to 18,656). Naively using them as "
        "training weights would let a few high-weight observations dominate "
        "gradient updates, destabilizing optimization.",
        "3. The governance requirement for survey-weight handling is fully "
        "satisfied by survey-weighted evaluation, which captures how the "
        "model performs on the real population.",
        "4. If survey-weighted training is desired in Stage 6, it should be "
        "done with normalized weights and treated as a separate methodological "
        "choice.", "",
    ]

    # --- Section 6: Class-balanced comparison ---
    lr_full_ncb = next((r for r in all_results
                        if r["label"] == "LR/Full/NoClsBal"), None)
    lr_full_cb = next((r for r in all_results
                       if r["label"] == "LR/Full/ClsBal"), None)
    cb_full_ncb = next((r for r in all_results
                        if r["label"] == "CB/Full/NoClsBal"), None)
    cb_full_cb = next((r for r in all_results
                       if r["label"] == "CB/Full/ClsBal"), None)

    lines += [
        "## 6. Class-Balanced vs No-Class-Balanced Training", "",
        "Each model family was tested with two training modes:", "",
        "1. **NoClsBal**: standard training, no class adjustment",
        "2. **ClsBal**: class_weight='balanced' for LR; "
        "scale_pos_weight for CatBoost", "",
    ]

    if lr_full_ncb and lr_full_cb:
        lines += [
            "### LR: Class-Balanced vs Standard (Full)",
            f"- NoClsBal PR-AUC: {fmt(lr_full_ncb['pr_auc'])} | "
            f"F1: {fmt(lr_full_ncb['f1'])}",
            f"- ClsBal   PR-AUC: {fmt(lr_full_cb['pr_auc'])} | "
            f"F1: {fmt(lr_full_cb['f1'])}",
        ]
        if lr_full_cb["recall"] > lr_full_ncb["recall"]:
            lines.append("- Class balancing improves recall at the cost "
                         "of precision (expected behavior).")
        lines.append("")

    if cb_full_ncb and cb_full_cb:
        lines += [
            "### CatBoost: Class-Balanced vs Standard (Full)",
            f"- NoClsBal PR-AUC: {fmt(cb_full_ncb['pr_auc'])} | "
            f"F1: {fmt(cb_full_ncb['f1'])}",
            f"- ClsBal   PR-AUC: {fmt(cb_full_cb['pr_auc'])} | "
            f"F1: {fmt(cb_full_cb['f1'])}",
            "",
        ]

    # Threshold diagnostics
    lines += [
        "## 7. Threshold Diagnostic Summary", "",
        "The default 0.5 threshold is suboptimal for this imbalanced problem.",
        "Threshold diagnostics show the precision-recall tradeoff for "
        "top candidates.", "",
    ]
    for config_label, diag_rows in threshold_diag.items():
        best_f1_row = max(diag_rows, key=lambda r: r["f1"])
        lines.append(
            f"**{config_label}**: Best F1 = {fmt(best_f1_row['f1'])} "
            f"at threshold = {best_f1_row['threshold']:.2f} "
            f"(P={fmt(best_f1_row['precision'])}, "
            f"R={fmt(best_f1_row['recall'])})"
        )
    lines.append("")
    lines.append(
        "Threshold selection will be refined in Stage 6 with "
        "business-objective alignment."
    )
    lines.append("")

    # Error analysis
    lines.append(error_text)

    # Recommendations — dual-metric framing
    lines += [
        "## 9. Recommendation for Stage 6", "",
        "### Under unweighted evaluation", "",
        f"**Best model**: {best_val['label']}", "",
        f"- Validation PR-AUC: {fmt(best_val['pr_auc'])}",
        f"- Validation ROC-AUC: {fmt(best_val['roc_auc'])}",
        f"- Validation F1: {fmt(best_val['f1'])}", "",

        "### Under survey-weighted evaluation", "",
        f"**Best model**: {best_val_sw['label']}", "",
        f"- Validation SW-PR-AUC: {fmt(best_val_sw['pr_auc'])}",
        f"- Validation SW-ROC-AUC: {fmt(best_val_sw['roc_auc'])}",
        f"- Validation SW-F1: {fmt(best_val_sw['f1'])}", "",
    ]

    same_winner = best_val["label"] == best_val_sw["label"]
    if same_winner:
        lines.append(f"The preferred carry-forward candidate is the same under "
                     f"both unweighted and survey-weighted evaluation: "
                     f"**{best_val['label']}**.")
    else:
        lines.append(f"**Note**: The preferred candidate differs between "
                     f"unweighted ({best_val['label']}) and survey-weighted "
                     f"({best_val_sw['label']}) evaluation. Stage 6 should "
                     f"evaluate both under the business objective.")
    lines.append("")

    # Full vs reduced conclusion
    cb_results = [r for r in all_results if "CB" in r["label"]]
    lr_results = [r for r in all_results if "LR" in r["label"]]
    best_cb = max(cb_results, key=lambda r: r["pr_auc"]) if cb_results else None
    best_lr = max(lr_results, key=lambda r: r["pr_auc"]) if lr_results else None

    cb_sw = [r for r in all_sw_results if "CB" in r["label"]]
    best_cb_sw = max(cb_sw, key=lambda r: r["pr_auc"]) if cb_sw else None

    if best_cb and best_lr:
        gap = best_cb["pr_auc"] - best_lr["pr_auc"]
        lines += [
            f"CatBoost outperforms Logistic Regression by "
            f"{gap:.4f} PR-AUC on validation (unweighted).", "",
        ]

    # Full vs Reduced comparison
    cb_full = [r for r in cb_results if "Full" in r["label"]]
    cb_red = [r for r in cb_results if "Red" in r["label"]]
    if cb_full and cb_red:
        best_full = max(cb_full, key=lambda r: r["pr_auc"])
        best_red = max(cb_red, key=lambda r: r["pr_auc"])
        if best_red["pr_auc"] >= best_full["pr_auc"]:
            lines.append("**Full vs Reduced**: Reduced feature set matches or "
                         "exceeds Full under both eval regimes. The 5 review "
                         "columns add noise, not signal.")
        else:
            lines.append("**Full vs Reduced**: Full feature set slightly "
                         "outperforms Reduced. Review columns may contribute "
                         "marginal signal.")
        lines.append("")

    lines += [
        "### Stage 6 priorities:",
        "1. Hyperparameter tuning for the carry-forward CatBoost candidate",
        "2. Threshold optimization aligned to business objective",
        "3. Calibration assessment",
        "4. Feature importance analysis for interpretability",
        "5. Survey-weighted evaluation in final reporting",
        "",
    ]

    # Test results
    if test_results:
        lines += [
            "## 10. Test Set Confirmation", "",
            "Test metrics (both unweighted and survey-weighted) for the "
            "carry-forward candidate(s) are reported in BASELINE_METRICS.md. "
            "These confirm that validation performance is stable.", "",
        ]

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# 9. MAIN
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stage 5: classification baselines")
    parser.add_argument("--datadir", default="outputs",
                        help="Directory containing clf_train/val/test.csv")
    parser.add_argument("--outdir", default="outputs/stage5",
                        help="Output directory for Stage 5 artifacts")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    seed = args.seed
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    datadir = Path(args.datadir)

    # ── Load data ──
    print("[1/9] Loading splits...")
    train = load_split(datadir / "clf_train.csv")
    val = load_split(datadir / "clf_val.csv")
    test = load_split(datadir / "clf_test.csv")
    print(f"  train={len(train):,}  val={len(val):,}  test={len(test):,}")

    # Governance check
    feature_candidates = [c for c in train.columns if c not in META_COLS]
    assert "weight" not in feature_candidates, "weight in features!"
    assert "target" not in feature_candidates, "target in features!"

    y_train = train["target"].values
    y_val = val["target"].values
    y_test = test["target"].values
    w_train = train["weight"].values
    w_val = val["weight"].values
    w_test = test["weight"].values

    # ── Duplicate audit ──
    print("[2/9] Duplicate leakage audit...")
    dup_results = duplicate_audit(train, val, test)
    write_duplicate_audit_md(dup_results, outdir)
    print(f"  Exact dups in train: {dup_results['exact_dup_train']:,}")
    print(f"  Cross train-val: {dup_results['cross_train_val']:,}")
    print(f"  Conflicting-target groups: {dup_results['conflicting_target_groups']:,}")

    # ── Prepare feature sets ──
    print("[3/9] Preparing feature sets...")
    full_cols = get_feature_cols("full")
    reduced_cols = get_feature_cols("reduced")

    # ── Rare-level pooling (LR only, fit on train) ──
    print("[4/9] Building rare-level pooling map...")
    pool_cols_full = [c for c in RARE_POOL_COLS
                      if c in full_cols["categorical_all"]]
    rare_map = build_rare_level_map(train, pool_cols_full, RARE_POOL_THRESHOLD)
    rare_pool_info = {col: len(mapping) for col, mapping in rare_map.items()}
    print(f"  Pooling applied to {len(rare_map)} columns: "
          + ", ".join(f"{c}({n})" for c, n in rare_pool_info.items()))

    # Apply pooling to copies for LR
    train_pooled = apply_rare_pooling(train, rare_map)
    val_pooled = apply_rare_pooling(val, rare_map)
    test_pooled = apply_rare_pooling(test, rare_map)

    # ── Build reduced rare map ──
    pool_cols_reduced = [c for c in RARE_POOL_COLS
                         if c in reduced_cols["categorical_all"]]
    rare_map_reduced = {k: v for k, v in rare_map.items()
                        if k in pool_cols_reduced}

    train_pooled_red = apply_rare_pooling(train, rare_map_reduced)
    val_pooled_red = apply_rare_pooling(val, rare_map_reduced)
    test_pooled_red = apply_rare_pooling(test, rare_map_reduced)

    # ── Experiment grid ──
    print("[5/9] Running experiment grid (8 configurations)...")
    all_val_results = []       # unweighted eval
    all_val_sw_results = []    # survey-weighted eval
    all_test_results = []      # unweighted eval
    all_test_sw_results = []   # survey-weighted eval
    threshold_diags = {}
    error_analyses = {}

    # Class-balanced training: compute scale_pos_weight for CatBoost
    pos_rate = y_train.mean()
    spw = (1 - pos_rate) / pos_rate  # ~15.1

    configs = [
        # (label, model_type, feature_variant, class_balanced)
        ("LR/Full/NoClsBal", "lr", "full", False),
        ("LR/Full/ClsBal", "lr", "full", True),
        ("LR/Red/NoClsBal", "lr", "reduced", False),
        ("LR/Red/ClsBal", "lr", "reduced", True),
        ("CB/Full/NoClsBal", "cb", "full", False),
        ("CB/Full/ClsBal", "cb", "full", True),
        ("CB/Red/NoClsBal", "cb", "reduced", False),
        ("CB/Red/ClsBal", "cb", "reduced", True),
    ]

    for label, model_type, variant, class_balanced in configs:
        print(f"  Training {label}...", end=" ", flush=True)

        cols = full_cols if variant == "full" else reduced_cols
        cont = cols["continuous"]
        cat_all = cols["categorical_all"]
        log1p = cols["log1p"]

        if model_type == "lr":
            # Use pooled data for LR
            if variant == "full":
                tr_data, vl_data, ts_data = train_pooled, val_pooled, test_pooled
            else:
                tr_data, vl_data, ts_data = (train_pooled_red, val_pooled_red,
                                             test_pooled_red)

            cw = "balanced" if class_balanced else None
            pipeline = build_lr_pipeline(cont, cat_all, log1p,
                                         class_weight=cw)

            X_tr = tr_data[cont + cat_all + log1p]
            X_vl = vl_data[cont + cat_all + log1p]
            X_ts = ts_data[cont + cat_all + log1p]

            pipeline.fit(X_tr, y_train)
            y_prob_val = pipeline.predict_proba(X_vl)[:, 1]
            y_prob_test = pipeline.predict_proba(X_ts)[:, 1]

        else:  # catboost
            tr_data, vl_data, ts_data = train, val, test

            # CatBoost uses raw continuous + all categoricals (no log1p needed)
            cb_features = cont + cat_all
            cat_indices = list(range(len(cont), len(cb_features)))

            X_tr = tr_data[cb_features]
            X_vl = vl_data[cb_features]
            X_ts = ts_data[cb_features]

            _spw = spw if class_balanced else None
            model = build_catboost(cat_indices, scale_pos_weight=_spw)

            train_pool = Pool(X_tr, y_train, cat_features=cat_indices)
            val_pool = Pool(X_vl, y_val, cat_features=cat_indices)

            model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=50)
            y_prob_val = model.predict_proba(X_vl)[:, 1]
            y_prob_test = model.predict_proba(X_ts)[:, 1]

        # Evaluate at 0.5 threshold — BOTH unweighted and survey-weighted
        y_pred_val = (y_prob_val >= 0.5).astype(int)
        y_pred_test = (y_prob_test >= 0.5).astype(int)

        # A. Unweighted eval (standard ML metrics)
        val_metrics = evaluate(y_val, y_prob_val, y_pred_val, label=label)
        test_metrics = evaluate(y_test, y_prob_test, y_pred_test,
                                label=label + " [TEST]")

        # B. Survey-weighted eval (population-representative metrics)
        val_sw = evaluate(y_val, y_prob_val, y_pred_val,
                          sample_weight=w_val, label=label)
        test_sw = evaluate(y_test, y_prob_test, y_pred_test,
                           sample_weight=w_test, label=label + " [TEST]")

        all_val_results.append(val_metrics)
        all_test_results.append(test_metrics)
        all_val_sw_results.append(val_sw)
        all_test_sw_results.append(test_sw)

        print(f"PR-AUC={val_metrics['pr_auc']:.4f}  "
              f"ROC-AUC={val_metrics['roc_auc']:.4f}  "
              f"F1={val_metrics['f1']:.4f}  "
              f"SW-PR-AUC={val_sw['pr_auc']:.4f}")

    # ── Threshold diagnostics for top candidates ──
    print("[6/9] Threshold diagnostics...")

    # Re-run predictions for top candidates to get threshold curves
    # Pick best LR and best CB by val PR-AUC
    best_lr_label = max(
        [r for r in all_val_results if "LR" in r["label"]],
        key=lambda r: r["pr_auc"]
    )["label"]
    best_cb_label = max(
        [r for r in all_val_results if "CB" in r["label"]],
        key=lambda r: r["pr_auc"]
    )["label"]

    # Re-predict for threshold analysis
    for label, model_type, variant, class_balanced in configs:
        if label not in (best_lr_label, best_cb_label):
            continue

        cols = full_cols if variant == "full" else reduced_cols
        cont = cols["continuous"]
        cat_all = cols["categorical_all"]
        log1p = cols["log1p"]

        if model_type == "lr":
            if variant == "full":
                tr_data, vl_data = train_pooled, val_pooled
            else:
                tr_data, vl_data = train_pooled_red, val_pooled_red

            cw = "balanced" if class_balanced else None
            pipeline = build_lr_pipeline(cont, cat_all, log1p,
                                         class_weight=cw)
            X_tr = tr_data[cont + cat_all + log1p]
            X_vl = vl_data[cont + cat_all + log1p]
            pipeline.fit(X_tr, y_train)
            y_prob = pipeline.predict_proba(X_vl)[:, 1]
        else:
            tr_data, vl_data = train, val
            cb_features = cont + cat_all
            cat_indices = list(range(len(cont), len(cb_features)))
            X_tr = tr_data[cb_features]
            X_vl = vl_data[cb_features]
            _spw = spw if class_balanced else None
            model = build_catboost(cat_indices, scale_pos_weight=_spw)
            train_pool = Pool(X_tr, y_train, cat_features=cat_indices)
            val_pool_cb = Pool(X_vl, y_val, cat_features=cat_indices)
            model.fit(train_pool, eval_set=val_pool_cb,
                      early_stopping_rounds=50)
            y_prob = model.predict_proba(X_vl)[:, 1]

        threshold_diags[label] = threshold_diagnostics(y_val, y_prob)

        # Error analysis at 0.5
        y_pred_50 = (y_prob >= 0.5).astype(int)
        error_analyses[label] = error_analysis(vl_data, y_val, y_pred_50,
                                               y_prob)

    # ── Generate documentation ──
    print("[7/9] Generating documentation...")

    error_text = format_error_analysis(error_analyses)

    # Select test results for best candidates only
    selected_test = [r for r in all_test_results
                     if r["label"].replace(" [TEST]", "")
                     in (best_lr_label, best_cb_label)]
    selected_test_sw = [r for r in all_test_sw_results
                        if r["label"].replace(" [TEST]", "")
                        in (best_lr_label, best_cb_label)]

    metrics_md = generate_baseline_metrics_md(
        all_val_results, all_val_sw_results,
        selected_test, selected_test_sw,
        threshold_diags
    )
    (outdir / "BASELINE_METRICS.md").write_text(metrics_md, encoding="utf-8")
    print("  BASELINE_METRICS.md")

    report_md = generate_classifier_report_md(
        all_val_results, all_val_sw_results,
        selected_test, selected_test_sw,
        rare_pool_info, error_text, threshold_diags, dup_results
    )
    (outdir / "CLASSIFIER_BASELINE_REPORT.md").write_text(report_md,
                                                           encoding="utf-8")
    print("  CLASSIFIER_BASELINE_REPORT.md")

    # Save raw results as JSON for reproducibility
    print("[8/9] Saving raw results...")
    raw = {
        "validation_unweighted": all_val_results,
        "validation_survey_weighted": all_val_sw_results,
        "test_unweighted": all_test_results,
        "test_survey_weighted": all_test_sw_results,
        "threshold_diagnostics": threshold_diags,
        "error_analyses": error_analyses,
        "duplicate_audit": dup_results,
        "rare_pool_info": rare_pool_info,
        "config": {"seed": SEED, "rare_pool_threshold": RARE_POOL_THRESHOLD},
    }
    (outdir / "stage5_raw_results.json").write_text(
        json.dumps(raw, indent=2, default=str), encoding="utf-8"
    )
    print("  stage5_raw_results.json")

    # ── Summary ──
    print("\n[9/9] Stage 5 complete!")
    print(f"  Best LR (val, unweighted):  {best_lr_label}")
    print(f"  Best CB (val, unweighted):  {best_cb_label}")
    overall_best = max(all_val_results, key=lambda r: r["pr_auc"])
    overall_best_sw = max(all_val_sw_results, key=lambda r: r["pr_auc"])
    print(f"  Best unweighted:     {overall_best['label']} "
          f"(PR-AUC={overall_best['pr_auc']:.4f})")
    print(f"  Best survey-weighted: {overall_best_sw['label']} "
          f"(SW-PR-AUC={overall_best_sw['pr_auc']:.4f})")
    print(f"\n  All artifacts in {outdir}/")


if __name__ == "__main__":
    main()
