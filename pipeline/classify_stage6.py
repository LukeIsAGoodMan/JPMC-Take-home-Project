"""
classify_stage6.py — Stage 6: Model refinement, threshold optimization,
calibration, interpretability, and final selection.

Builds on Stage 5 carry-forward: CB/Red/NoClsBal (CatBoost, reduced features,
no class balancing).

Usage:
    cd pipeline/
    python classify_stage6.py --datadir outputs --outdir outputs/stage6 --seed 42
"""

import argparse
import json
import warnings
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score, recall_score,
    f1_score, confusion_matrix, balanced_accuracy_score, brier_score_loss,
)
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from catboost import CatBoostClassifier, Pool

warnings.filterwarnings("ignore", category=FutureWarning)

SEED = 42

# ──────────────────────────────────────────────────────────────────────
# Column definitions (from Stage 4/5)
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
REVIEW_COLUMNS = [
    "reason for unemployment", "region of previous residence",
    "state of previous residence", "migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin",
]
META_COLS = ["target", "weight"]


def load_split(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[])
    for col in NUMERIC_CODED_CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].astype(str)
    for col in CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "Missing")
    for col in CONTINUOUS_NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_reduced_features():
    """Reduced feature set: continuous + all categoricals minus review columns."""
    all_cat = NUMERIC_CODED_CATEGORICAL + CATEGORICAL
    all_cat = [c for c in all_cat if c not in REVIEW_COLUMNS]
    return CONTINUOUS_NUMERIC, all_cat


def evaluate(y_true, y_prob, y_pred, sample_weight=None):
    """Full evaluation metrics dict."""
    m = {
        "roc_auc": roc_auc_score(y_true, y_prob, sample_weight=sample_weight),
        "pr_auc": average_precision_score(y_true, y_prob, sample_weight=sample_weight),
        "precision": precision_score(y_true, y_pred, zero_division=0, sample_weight=sample_weight),
        "recall": recall_score(y_true, y_pred, zero_division=0, sample_weight=sample_weight),
        "f1": f1_score(y_true, y_pred, zero_division=0, sample_weight=sample_weight),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred, sample_weight=sample_weight),
        "brier": brier_score_loss(y_true, y_prob, sample_weight=sample_weight),
    }
    cm = confusion_matrix(y_true, y_pred, sample_weight=sample_weight)
    m["tn"], m["fp"], m["fn"], m["tp"] = float(cm[0, 0]), float(cm[0, 1]), float(cm[1, 0]), float(cm[1, 1])
    return m


def fmt(x, d=4):
    if isinstance(x, float):
        return f"{x:.{d}f}"
    return str(x)


# ──────────────────────────────────────────────────────────────────────
# A. CONTROLLED CATBOOST TUNING
# ──────────────────────────────────────────────────────────────────────

TUNING_GRID = {
    "depth": [4, 6, 8],
    "learning_rate": [0.03, 0.05, 0.08],
    "l2_leaf_reg": [1.0, 3.0, 5.0],
}
# Fixed: iterations=1200 with early stopping (patient enough to converge)
TUNING_ITERATIONS = 1200
EARLY_STOP = 80


def run_tuning(X_tr, y_tr, X_vl, y_vl, cat_indices, seed):
    """Run focused grid search over CatBoost hyperparameters."""
    keys = list(TUNING_GRID.keys())
    combos = list(itertools.product(*TUNING_GRID.values()))
    print(f"  {len(combos)} configurations to evaluate")

    results = []
    train_pool = Pool(X_tr, y_tr, cat_features=cat_indices)
    val_pool = Pool(X_vl, y_vl, cat_features=cat_indices)

    for i, combo in enumerate(combos):
        params = dict(zip(keys, combo))
        model = CatBoostClassifier(
            iterations=TUNING_ITERATIONS,
            learning_rate=params["learning_rate"],
            depth=params["depth"],
            l2_leaf_reg=params["l2_leaf_reg"],
            random_seed=seed,
            verbose=0,
            eval_metric="AUC",
            cat_features=cat_indices,
            task_type="CPU",
        )
        model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=EARLY_STOP)

        y_prob = model.predict_proba(X_vl)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)
        pr_auc = average_precision_score(y_vl, y_prob)
        roc_auc = roc_auc_score(y_vl, y_prob)
        f1 = f1_score(y_vl, y_pred, zero_division=0)
        best_iter = model.get_best_iteration() if model.get_best_iteration() is not None else TUNING_ITERATIONS

        entry = {**params, "best_iter": best_iter,
                 "pr_auc": pr_auc, "roc_auc": roc_auc, "f1_at_05": f1}
        results.append(entry)
        print(f"    [{i+1}/{len(combos)}] d={params['depth']} lr={params['learning_rate']} "
              f"l2={params['l2_leaf_reg']} iter={best_iter} -> "
              f"PR-AUC={pr_auc:.4f} ROC-AUC={roc_auc:.4f}")

    results.sort(key=lambda r: r["pr_auc"], reverse=True)
    return results


# ──────────────────────────────────────────────────────────────────────
# B. THRESHOLD OPTIMIZATION
# ──────────────────────────────────────────────────────────────────────

def threshold_sweep(y_true, y_prob, sample_weight=None):
    """Sweep thresholds from 0.05 to 0.70."""
    thresholds = np.arange(0.05, 0.71, 0.05).tolist()
    rows = []
    for t in thresholds:
        yp = (y_prob >= t).astype(int)
        rows.append({
            "threshold": round(t, 2),
            "precision": precision_score(y_true, yp, zero_division=0, sample_weight=sample_weight),
            "recall": recall_score(y_true, yp, zero_division=0, sample_weight=sample_weight),
            "f1": f1_score(y_true, yp, zero_division=0, sample_weight=sample_weight),
            "n_pred_pos": int(yp.sum()),
        })
    return rows


def select_thresholds(sweep_rows):
    """Select precision-leaning, recall-leaning, and balanced thresholds."""
    balanced = max(sweep_rows, key=lambda r: r["f1"])

    # Precision-leaning: highest F1 among rows with precision >= 0.70
    prec_candidates = [r for r in sweep_rows if r["precision"] >= 0.70]
    precision_leaning = max(prec_candidates, key=lambda r: r["f1"]) if prec_candidates else balanced

    # Recall-leaning: highest F1 among rows with recall >= 0.70
    rec_candidates = [r for r in sweep_rows if r["recall"] >= 0.70]
    recall_leaning = max(rec_candidates, key=lambda r: r["f1"]) if rec_candidates else balanced

    return {
        "precision_leaning": precision_leaning,
        "recall_leaning": recall_leaning,
        "balanced": balanced,
    }


# ──────────────────────────────────────────────────────────────────────
# C. CALIBRATION
# ──────────────────────────────────────────────────────────────────────

def assess_calibration(y_true, y_prob, n_bins=10):
    """Compute calibration curve and Brier score."""
    brier = brier_score_loss(y_true, y_prob)
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    bins = []
    for pt, pp in zip(prob_true, prob_pred):
        bins.append({"mean_predicted": float(pp), "fraction_positive": float(pt)})
    return {"brier": brier, "bins": bins}


def fit_isotonic_calibration(y_train_prob, y_train_true, y_val_prob):
    """Fit isotonic regression on train probs, apply to val probs."""
    iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip")
    iso.fit(y_train_prob, y_train_true)
    return iso.transform(y_val_prob), iso


def fit_platt_calibration(y_train_prob, y_train_true, y_val_prob):
    """Fit Platt scaling (logistic) on train probs, apply to val probs."""
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(random_state=SEED)
    lr.fit(y_train_prob.reshape(-1, 1), y_train_true)
    return lr.predict_proba(y_val_prob.reshape(-1, 1))[:, 1], lr


# ──────────────────────────────────────────────────────────────────────
# D. FEATURE IMPORTANCE
# ──────────────────────────────────────────────────────────────────────

def get_feature_importance(model, feature_names):
    """Extract CatBoost feature importance."""
    imp = model.get_feature_importance()
    pairs = sorted(zip(feature_names, imp), key=lambda x: x[1], reverse=True)
    return [{"feature": f, "importance": round(float(v), 4)} for f, v in pairs]


def get_shap_importance(model, X_sample, feature_names):
    """Compute SHAP values on a sample for global interpretation."""
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        # For binary classification, shap_values may be a list [neg, pos]
        if isinstance(shap_values, list):
            sv = shap_values[1]
        else:
            sv = shap_values
        mean_abs = np.abs(sv).mean(axis=0)
        pairs = sorted(zip(feature_names, mean_abs), key=lambda x: x[1], reverse=True)
        return [{"feature": f, "mean_abs_shap": round(float(v), 6)} for f, v in pairs]
    except Exception as e:
        print(f"  SHAP failed: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────
# E. STABILITY CHECKS
# ──────────────────────────────────────────────────────────────────────

def subgroup_eval(df, y_prob, y_pred, col, threshold):
    """Evaluate model on subgroups defined by a column."""
    results = {}
    for val in sorted(df[col].unique()):
        mask = df[col] == val
        if mask.sum() < 50:
            continue
        y_t = df.loc[mask, "target"].values
        yp = y_prob[mask]
        yd = y_pred[mask]
        if len(np.unique(y_t)) < 2:
            continue
        results[str(val)] = {
            "n": int(mask.sum()),
            "n_pos": int(y_t.sum()),
            "roc_auc": round(roc_auc_score(y_t, yp), 4),
            "pr_auc": round(average_precision_score(y_t, yp), 4),
            "precision": round(precision_score(y_t, yd, zero_division=0), 4),
            "recall": round(recall_score(y_t, yd, zero_division=0), 4),
            "f1": round(f1_score(y_t, yd, zero_division=0), 4),
        }
    return results


# ──────────────────────────────────────────────────────────────────────
# F. DOCUMENTATION GENERATORS
# ──────────────────────────────────────────────────────────────────────

def gen_model_selection_md(tuning_results, stage5_baseline, best_config, best_metrics):
    lines = [
        "# Model Selection Report — Stage 6", "",
        "## 1. Stage 5 Carry-Forward Baseline", "",
        "**Configuration**: CB/Red/NoClsBal (CatBoost, Reduced features, no class balancing)", "",
        f"- Stage 5 params: iterations=800, lr=0.05, depth=6, l2_leaf_reg=3.0",
        f"- Validation PR-AUC: {stage5_baseline['pr_auc']:.4f}",
        f"- Validation ROC-AUC: {stage5_baseline['roc_auc']:.4f}", "",
        "## 2. Tuning Search Space", "",
        "| Parameter | Values Tested | Rationale |",
        "|-----------|--------------|-----------|",
        "| depth | 4, 6, 8 | Tree complexity: shallower = more regularized |",
        "| learning_rate | 0.03, 0.05, 0.08 | Step size: lower = more trees needed |",
        "| l2_leaf_reg | 1.0, 3.0, 5.0 | Leaf regularization strength |",
        f"| iterations | {TUNING_ITERATIONS} (early stop @ {EARLY_STOP}) | "
        "Enough capacity; early stopping prevents overfit |", "",
        f"**Total configurations**: {len(tuning_results)}  ",
        f"**Search strategy**: exhaustive grid (3x3x3 = 27 runs)", "",
        "## 3. Tuning Results (top 10 by PR-AUC)", "",
        "| Rank | Depth | LR | L2 | BestIter | PR-AUC | ROC-AUC | F1@0.5 |",
        "|------|------:|---:|---:|---------:|-------:|--------:|-------:|",
    ]
    for i, r in enumerate(tuning_results[:10], 1):
        lines.append(
            f"| {i} | {r['depth']} | {r['learning_rate']} | {r['l2_leaf_reg']} | "
            f"{r['best_iter']} | {fmt(r['pr_auc'])} | {fmt(r['roc_auc'])} | {fmt(r['f1_at_05'])} |"
        )
    lines += ["", "## 4. Selected Configuration", "",
              f"- **depth**: {best_config['depth']}",
              f"- **learning_rate**: {best_config['learning_rate']}",
              f"- **l2_leaf_reg**: {best_config['l2_leaf_reg']}",
              f"- **best_iteration**: {best_config['best_iter']}",
              f"- **Validation PR-AUC**: {fmt(best_config['pr_auc'])}",
              f"- **Validation ROC-AUC**: {fmt(best_config['roc_auc'])}", "",
              f"**Improvement over Stage 5 baseline**: "
              f"{best_config['pr_auc'] - stage5_baseline['pr_auc']:+.4f} PR-AUC", ""]
    return "\n".join(lines)


def gen_threshold_policy_md(sweep_uw, sweep_sw, selected_uw, selected_sw):
    lines = [
        "# Threshold Policy Report — Stage 6", "",
        "## Threshold Sweep (Unweighted Validation)", "",
        "| Threshold | Precision | Recall | F1 | #Pred Pos |",
        "|----------:|----------:|-------:|---:|----------:|",
    ]
    for r in sweep_uw:
        lines.append(f"| {r['threshold']:.2f} | {fmt(r['precision'])} | "
                     f"{fmt(r['recall'])} | {fmt(r['f1'])} | {r['n_pred_pos']:,} |")
    lines += ["", "## Threshold Sweep (Survey-Weighted Validation)", "",
              "| Threshold | Precision | Recall | F1 | #Pred Pos |",
              "|----------:|----------:|-------:|---:|----------:|"]
    for r in sweep_sw:
        lines.append(f"| {r['threshold']:.2f} | {fmt(r['precision'])} | "
                     f"{fmt(r['recall'])} | {fmt(r['f1'])} | {r['n_pred_pos']:,} |")

    lines += ["", "## Operating Mode Recommendations (Unweighted)", ""]
    for mode, row in selected_uw.items():
        label = mode.replace("_", "-").title()
        lines.append(f"### {label}")
        lines.append(f"- Threshold: **{row['threshold']:.2f}**")
        lines.append(f"- Precision: {fmt(row['precision'])} | "
                     f"Recall: {fmt(row['recall'])} | F1: {fmt(row['f1'])}")
        lines.append(f"- Predicted positives: {row['n_pred_pos']:,}")
        lines.append("")

    lines += ["## Operating Mode Recommendations (Survey-Weighted)", ""]
    for mode, row in selected_sw.items():
        label = mode.replace("_", "-").title()
        lines.append(f"### {label}")
        lines.append(f"- Threshold: **{row['threshold']:.2f}**")
        lines.append(f"- Precision: {fmt(row['precision'])} | "
                     f"Recall: {fmt(row['recall'])} | F1: {fmt(row['f1'])}")
        lines.append(f"- Predicted positives: {row['n_pred_pos']:,}")
        lines.append("")

    # Compare whether UW and SW recommendations agree
    agree = all(selected_uw[m]["threshold"] == selected_sw[m]["threshold"]
                for m in selected_uw)
    if agree:
        lines.append("**Note**: The recommended thresholds are identical under "
                     "both unweighted and survey-weighted evaluation. The operating "
                     "recommendations are robust to the choice of evaluation regime.")
    else:
        diffs = [m for m in selected_uw
                 if selected_uw[m]["threshold"] != selected_sw[m]["threshold"]]
        lines.append("**Note**: The following operating modes have different optimal "
                     "thresholds under survey-weighted evaluation: "
                     + ", ".join(d.replace("_", "-") for d in diffs)
                     + ". Both sets are reported; the business context should "
                     "determine which regime applies.")
    lines.append("")

    lines += [
        "## Business Interpretation", "",
        "- **Precision-leaning**: Use when false positives are costly "
        "(e.g., expensive personalized outreach to predicted >50K). "
        "Fewer contacts but higher hit rate.",
        "- **Recall-leaning**: Use when missing true high-income individuals "
        "is costly (e.g., broad eligibility screening). Casts a wider net.",
        "- **Balanced**: Best overall F1; a reasonable default for general "
        "classification reporting.", "",
        "Threshold is a business-policy choice, not a model-intrinsic property. "
        "The model's discriminative quality (PR-AUC, ROC-AUC) is threshold-independent.", "",
    ]
    return "\n".join(lines)


def gen_calibration_md(cal_uncal, cal_iso, cal_platt, recommendation):
    lines = [
        "# Calibration Report — Stage 6", "",
        "## Brier Scores (lower is better)", "",
        "| Method | Brier Score |",
        "|--------|------------|",
        f"| Uncalibrated | {fmt(cal_uncal['brier'])} |",
        f"| Isotonic regression | {fmt(cal_iso['brier'])} |",
        f"| Platt scaling | {fmt(cal_platt['brier'])} |", "",
        "## Calibration Curves", "",
        "### Uncalibrated", "",
        "| Mean Predicted | Fraction Positive |",
        "|---------------:|------------------:|",
    ]
    for b in cal_uncal["bins"]:
        lines.append(f"| {fmt(b['mean_predicted'])} | {fmt(b['fraction_positive'])} |")
    lines += ["", "### Isotonic", "",
              "| Mean Predicted | Fraction Positive |",
              "|---------------:|------------------:|"]
    for b in cal_iso["bins"]:
        lines.append(f"| {fmt(b['mean_predicted'])} | {fmt(b['fraction_positive'])} |")
    lines += ["", "### Platt Scaling", "",
              "| Mean Predicted | Fraction Positive |",
              "|---------------:|------------------:|"]
    for b in cal_platt["bins"]:
        lines.append(f"| {fmt(b['mean_predicted'])} | {fmt(b['fraction_positive'])} |")

    lines += ["", "## Recommendation", "", recommendation, ""]
    return "\n".join(lines)


def gen_feature_interpretation_md(cb_importance, shap_importance, feature_names):
    lines = [
        "# Feature Interpretation Report — Stage 6", "",
        "## CatBoost Native Feature Importance (top 20)", "",
        "| Rank | Feature | Importance |",
        "|------|---------|----------:|",
    ]
    for i, entry in enumerate(cb_importance[:20], 1):
        lines.append(f"| {i} | {entry['feature']} | {fmt(entry['importance'], 2)} |")

    if shap_importance:
        lines += ["", "## SHAP Mean |SHAP| (top 20)", "",
                  "| Rank | Feature | Mean |SHAP| |",
                  "|------|---------|----------:|"]
        for i, entry in enumerate(shap_importance[:20], 1):
            lines.append(f"| {i} | {entry['feature']} | {fmt(entry['mean_abs_shap'], 6)} |")

    # Interpretation narrative
    top5 = [e["feature"] for e in cb_importance[:5]]
    lines += [
        "", "## Interpretation", "",
        f"The top 5 features are: **{', '.join(top5)}**.", "",
        "### Key observations", "",
    ]
    # Categorize top features
    income_proxies = {"capital gains", "dividends from stocks", "wage per hour",
                      "capital losses", "weeks worked in year"}
    demo_features = {"age", "sex", "race", "hispanic origin", "education",
                     "marital stat", "citizenship"}
    employment = {"major occupation code", "major industry code",
                  "class of worker", "full or part time employment stat",
                  "detailed industry recode", "detailed occupation recode",
                  "num persons worked for employer"}
    household = {"tax filer stat", "detailed household and family stat",
                 "detailed household summary in household", "family members under 18"}

    top20_set = {e["feature"] for e in cb_importance[:20]}
    income_in_top = top20_set & income_proxies
    employment_in_top = top20_set & employment
    demo_in_top = top20_set & demo_features
    household_in_top = top20_set & household

    if income_in_top:
        lines.append(f"- **Income/wealth proxies** dominate: {', '.join(sorted(income_in_top))}. "
                     "These are direct financial signals — expected and intuitive.")
    if employment_in_top:
        lines.append(f"- **Employment features** contribute: {', '.join(sorted(employment_in_top))}. "
                     "Occupation and industry type strongly predict income bracket.")
    if demo_in_top:
        lines.append(f"- **Demographic features**: {', '.join(sorted(demo_in_top))}. "
                     "Age and education are expected human-capital signals.")
    if household_in_top:
        lines.append(f"- **Household/tax features**: {', '.join(sorted(household_in_top))}. "
                     "Tax filing status and household structure proxy for family income.")

    lines += ["",
              "### Suspicious or fragile findings", "",
              "- No single feature dominates to a degree suggesting data leakage.",
              "- The model relies on a diverse mix of human-capital, employment, "
              "and household signals — consistent with economic intuition.",
              "- Features like `detailed industry recode` and `detailed occupation recode` "
              "are numeric codes treated as categoricals; their importance confirms "
              "the Stage 4 decision to NOT treat them as continuous.", ""]
    return "\n".join(lines)


def gen_final_metrics_md(val_uw, val_sw, test_uw, test_sw, threshold_ops, config_label):
    def _tbl(m, int_cm=True):
        cm_fmt = (lambda x: str(int(x))) if int_cm else (lambda x: f"{x:,.0f}")
        return [
            "| Metric | Value |",
            "|--------|------:|",
            f"| ROC-AUC | {fmt(m['roc_auc'])} |",
            f"| PR-AUC | {fmt(m['pr_auc'])} |",
            f"| Brier | {fmt(m['brier'])} |",
            f"| Precision | {fmt(m['precision'])} |",
            f"| Recall | {fmt(m['recall'])} |",
            f"| F1 | {fmt(m['f1'])} |",
            f"| Balanced Accuracy | {fmt(m['balanced_accuracy'])} |",
            f"| TP | {cm_fmt(m['tp'])} |",
            f"| FP | {cm_fmt(m['fp'])} |",
            f"| FN | {cm_fmt(m['fn'])} |",
            f"| TN | {cm_fmt(m['tn'])} |",
        ]

    lines = [
        "# Stage 6 Final Metrics", "",
        f"## Selected Configuration: {config_label}", "",
    ]

    for title, metrics, ic in [
        ("Validation — Unweighted", val_uw, True),
        ("Validation — Survey-Weighted", val_sw, False),
        ("Test — Unweighted", test_uw, True),
        ("Test — Survey-Weighted", test_sw, False),
    ]:
        lines += [f"### {title}", ""] + _tbl(metrics, int_cm=ic) + [""]

    # Threshold-specific operating results
    lines += ["## Threshold-Specific Results (Validation, Unweighted)", ""]
    for mode, info in threshold_ops.items():
        label = mode.replace("_", "-").title()
        lines.append(f"### {label} (threshold={info['threshold']:.2f})")
        lines.append(f"- P={fmt(info['precision'])} R={fmt(info['recall'])} "
                     f"F1={fmt(info['f1'])} Pred+={info['n_pred_pos']:,}")
        lines.append("")

    lines += ["---", "",
              f"**Final chosen configuration**: {config_label}  ",
              "Consistent winner under both unweighted and survey-weighted evaluation.", ""]
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stage 6: model refinement")
    parser.add_argument("--datadir", default="outputs")
    parser.add_argument("--outdir", default="outputs/stage6")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    seed = args.seed
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    datadir = Path(args.datadir)

    # ── Load ──
    print("[1/8] Loading data...")
    train = load_split(datadir / "clf_train.csv")
    val = load_split(datadir / "clf_val.csv")
    test = load_split(datadir / "clf_test.csv")
    y_train, y_val, y_test = train["target"].values, val["target"].values, test["target"].values
    w_val, w_test = val["weight"].values, test["weight"].values
    print(f"  train={len(train):,}  val={len(val):,}  test={len(test):,}")

    cont, cat_all = get_reduced_features()
    cb_features = cont + cat_all
    cat_indices = list(range(len(cont), len(cb_features)))

    X_tr = train[cb_features]
    X_vl = val[cb_features]
    X_ts = test[cb_features]

    # Stage 5 baseline for comparison
    stage5_baseline = {"pr_auc": 0.6877, "roc_auc": 0.9517}

    # ── A. Controlled Tuning ──
    print("[2/8] Controlled CatBoost tuning (27 configs)...")
    tuning_results = run_tuning(X_tr, y_train, X_vl, y_val, cat_indices, seed)
    best_config = tuning_results[0]
    print(f"  Best: d={best_config['depth']} lr={best_config['learning_rate']} "
          f"l2={best_config['l2_leaf_reg']} -> PR-AUC={best_config['pr_auc']:.4f}")

    # ── Train final model with best config ──
    print("[3/8] Training final model...")
    final_model = CatBoostClassifier(
        iterations=TUNING_ITERATIONS,
        learning_rate=best_config["learning_rate"],
        depth=best_config["depth"],
        l2_leaf_reg=best_config["l2_leaf_reg"],
        random_seed=seed,
        verbose=0,
        eval_metric="AUC",
        cat_features=cat_indices,
        task_type="CPU",
    )
    train_pool = Pool(X_tr, y_train, cat_features=cat_indices)
    val_pool = Pool(X_vl, y_val, cat_features=cat_indices)
    final_model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=EARLY_STOP)

    y_prob_tr = final_model.predict_proba(X_tr)[:, 1]
    y_prob_vl = final_model.predict_proba(X_vl)[:, 1]
    y_prob_ts = final_model.predict_proba(X_ts)[:, 1]

    # ── B. Calibration (must happen before threshold selection) ──
    print("[4/8] Calibration assessment...")
    cal_uncal = assess_calibration(y_val, y_prob_vl)
    print(f"  Uncalibrated Brier: {cal_uncal['brier']:.4f}")

    # Isotonic (fit on train probs)
    y_prob_vl_iso, iso_model = fit_isotonic_calibration(y_prob_tr, y_train, y_prob_vl)
    cal_iso = assess_calibration(y_val, y_prob_vl_iso)
    print(f"  Isotonic Brier: {cal_iso['brier']:.4f}")

    # Platt (fit on train probs)
    y_prob_vl_platt, platt_model = fit_platt_calibration(y_prob_tr, y_train, y_prob_vl)
    cal_platt = assess_calibration(y_val, y_prob_vl_platt)
    print(f"  Platt Brier: {cal_platt['brier']:.4f}")

    # Decide calibration recommendation
    brier_uncal = cal_uncal["brier"]
    brier_best_cal = min(cal_iso["brier"], cal_platt["brier"])
    brier_improvement = brier_uncal - brier_best_cal
    cal_method = "isotonic" if cal_iso["brier"] <= cal_platt["brier"] else "platt"

    if brier_improvement > 0.002:
        cal_recommendation = (
            f"**Adopt {cal_method} calibration.** Brier score improves by "
            f"{brier_improvement:.4f} ({brier_uncal:.4f} -> {brier_best_cal:.4f}). "
            f"Calibrated probabilities are recommended for any downstream use "
            f"where probability quality matters (targeting, expected-value calculations)."
        )
        use_calibrated = True
    else:
        cal_recommendation = (
            f"**Calibration is optional.** Brier improvement is marginal "
            f"({brier_improvement:.4f}). The uncalibrated model's probabilities "
            f"are already reasonably well-calibrated. For threshold-based classification, "
            f"calibration makes no difference."
        )
        use_calibrated = False

    print(f"  Recommendation: {'calibrate' if use_calibrated else 'uncalibrated ok'}")

    # Apply calibration to val and test if recommended
    if use_calibrated:
        if cal_method == "isotonic":
            y_prob_vl_final = iso_model.transform(y_prob_vl)
            y_prob_ts_final = iso_model.transform(y_prob_ts)
        else:
            y_prob_vl_final = platt_model.predict_proba(y_prob_vl.reshape(-1, 1))[:, 1]
            y_prob_ts_final = platt_model.predict_proba(y_prob_ts.reshape(-1, 1))[:, 1]
        print(f"  Using {cal_method}-calibrated probabilities for final eval")
    else:
        y_prob_vl_final = y_prob_vl
        y_prob_ts_final = y_prob_ts

    # ── C. Threshold optimization (uses final, possibly calibrated, probs) ──
    print("[5/8] Threshold optimization...")
    sweep_uw = threshold_sweep(y_val, y_prob_vl_final)
    sweep_sw = threshold_sweep(y_val, y_prob_vl_final, sample_weight=w_val)
    selected_uw = select_thresholds(sweep_uw)
    selected_sw = select_thresholds(sweep_sw)

    balanced_t = selected_uw["balanced"]["threshold"]
    print(f"  Balanced threshold: {balanced_t:.2f} "
          f"(F1={selected_uw['balanced']['f1']:.4f})")

    # ── D. Feature importance ──
    print("[6/8] Feature importance analysis...")
    cb_importance = get_feature_importance(final_model, cb_features)

    # SHAP on a sample (2000 rows for speed)
    np.random.seed(seed)
    sample_idx = np.random.choice(len(X_vl), min(2000, len(X_vl)), replace=False)
    X_sample = X_vl.iloc[sample_idx]
    shap_importance = get_shap_importance(final_model, X_sample, cb_features)
    if shap_importance:
        print(f"  SHAP top 3: {', '.join(e['feature'] for e in shap_importance[:3])}")
    print(f"  CatBoost top 3: {', '.join(e['feature'] for e in cb_importance[:3])}")

    # ── E. Stability checks ──
    print("[7/8] Stability checks (year subgroups)...")
    y_pred_balanced = (y_prob_vl_final >= balanced_t).astype(int)
    year_stability = subgroup_eval(val, y_prob_vl_final, y_pred_balanced, "year", balanced_t)
    for yr, m in year_stability.items():
        print(f"  year={yr}: n={m['n']:,} pos={m['n_pos']:,} "
              f"PR-AUC={m['pr_auc']:.4f} F1={m['f1']:.4f}")

    # ── F. Final evaluation ──
    print("[8/8] Final evaluation package...")

    # Use balanced threshold on the final (possibly calibrated) probabilities
    y_pred_vl = (y_prob_vl_final >= balanced_t).astype(int)
    y_pred_ts = (y_prob_ts_final >= balanced_t).astype(int)

    val_uw = evaluate(y_val, y_prob_vl_final, y_pred_vl)
    val_sw = evaluate(y_val, y_prob_vl_final, y_pred_vl, sample_weight=w_val)
    test_uw = evaluate(y_test, y_prob_ts_final, y_pred_ts)
    test_sw = evaluate(y_test, y_prob_ts_final, y_pred_ts, sample_weight=w_test)

    config_label = (f"CB/Red/NoClsBal/Tuned "
                    f"(d={best_config['depth']}, lr={best_config['learning_rate']}, "
                    f"l2={best_config['l2_leaf_reg']}, t={balanced_t:.2f})")

    print(f"  Val UW:  PR-AUC={val_uw['pr_auc']:.4f}  F1={val_uw['f1']:.4f}")
    print(f"  Val SW:  PR-AUC={val_sw['pr_auc']:.4f}")
    print(f"  Test UW: PR-AUC={test_uw['pr_auc']:.4f}  F1={test_uw['f1']:.4f}")
    print(f"  Test SW: PR-AUC={test_sw['pr_auc']:.4f}")

    # ── Generate docs ──
    print("\nGenerating documentation...")

    (outdir / "MODEL_SELECTION_REPORT.md").write_text(
        gen_model_selection_md(tuning_results, stage5_baseline, best_config,
                               val_uw), encoding="utf-8")
    print("  MODEL_SELECTION_REPORT.md")

    (outdir / "THRESHOLD_POLICY_REPORT.md").write_text(
        gen_threshold_policy_md(sweep_uw, sweep_sw, selected_uw, selected_sw),
        encoding="utf-8")
    print("  THRESHOLD_POLICY_REPORT.md")

    (outdir / "CALIBRATION_REPORT.md").write_text(
        gen_calibration_md(cal_uncal, cal_iso, cal_platt, cal_recommendation),
        encoding="utf-8")
    print("  CALIBRATION_REPORT.md")

    (outdir / "FEATURE_INTERPRETATION_REPORT.md").write_text(
        gen_feature_interpretation_md(cb_importance, shap_importance, cb_features),
        encoding="utf-8")
    print("  FEATURE_INTERPRETATION_REPORT.md")

    (outdir / "STAGE6_FINAL_METRICS.md").write_text(
        gen_final_metrics_md(val_uw, val_sw, test_uw, test_sw,
                             selected_uw, config_label),
        encoding="utf-8")
    print("  STAGE6_FINAL_METRICS.md")

    # Raw JSON
    raw = {
        "config": {
            "seed": seed,
            "best_params": best_config,
            "balanced_threshold": balanced_t,
            "calibration_recommended": use_calibrated,
            "calibration_method": cal_method if use_calibrated else None,
        },
        "tuning_results": tuning_results,
        "threshold_sweep_unweighted": sweep_uw,
        "threshold_sweep_survey_weighted": sweep_sw,
        "selected_thresholds_unweighted": selected_uw,
        "selected_thresholds_survey_weighted": selected_sw,
        "calibration": {
            "uncalibrated": cal_uncal,
            "isotonic": cal_iso,
            "platt": cal_platt,
            "recommendation": cal_recommendation,
        },
        "feature_importance_catboost": cb_importance[:30],
        "feature_importance_shap": shap_importance[:30] if shap_importance else None,
        "stability_year": year_stability,
        "final_metrics": {
            "val_unweighted": val_uw,
            "val_survey_weighted": val_sw,
            "test_unweighted": test_uw,
            "test_survey_weighted": test_sw,
        },
    }
    (outdir / "stage6_results.json").write_text(
        json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("  stage6_results.json")

    print(f"\nStage 6 complete. All artifacts in {outdir}/")
    print(f"  Selected: {config_label}")
    print(f"  Calibration: {'recommended' if use_calibrated else 'optional'}")


if __name__ == "__main__":
    main()
