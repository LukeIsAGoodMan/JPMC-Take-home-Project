"""
v2_compute.py — V2 empirical computations.
Produces score-band analysis and second-pass segmentation within
the working-age segment, using the frozen V1 model and data.

Usage:
    cd v2/
    python -u v2_compute.py
"""

import json
import sys
import warnings
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool
from kmodes.kprototypes import KPrototypes

warnings.filterwarnings("ignore")
SEED = 42
PIPELINE = Path("../pipeline")
OUTDIR = Path(".")

# ── Column defs (from V1) ──
CONTINUOUS_NUMERIC = [
    "age", "wage per hour", "capital gains", "capital losses",
    "dividends from stocks", "num persons worked for employer",
    "weeks worked in year",
]
NUMERIC_CODED_CAT = [
    "detailed industry recode", "detailed occupation recode",
    "own business or self employed", "veterans benefits", "year",
]
CATEGORICAL = [
    "class of worker", "education", "enroll in edu inst last wk",
    "marital stat", "major industry code", "major occupation code",
    "race", "hispanic origin", "sex", "member of a labor union",
    "full or part time employment stat", "tax filer stat",
    "detailed household and family stat",
    "detailed household summary in household",
    "migration code-change in msa", "migration code-change in reg",
    "migration code-move within reg", "live in this house 1 year ago",
    "migration prev res in sunbelt", "family members under 18",
    "country of birth father", "country of birth mother",
    "country of birth self", "citizenship",
]
REVIEW_COLUMNS = [
    "reason for unemployment", "region of previous residence",
    "state of previous residence", "migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin",
]


def load_split(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[])
    for col in NUMERIC_CODED_CAT:
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
    all_cat = NUMERIC_CODED_CAT + [c for c in CATEGORICAL if c not in REVIEW_COLUMNS]
    return CONTINUOUS_NUMERIC, all_cat


# ═══════════════════════════════════════════════════════
# PART 1: SCORE-BAND ANALYSIS
# ═══════════════════════════════════════════════════════

def score_band_analysis():
    print("=" * 60)
    print("PART 1: Score-Band Analysis")
    print("=" * 60)

    # Load val set and retrain V1 model to get predictions
    print("[1] Loading data...")
    train = load_split(PIPELINE / "outputs/clf_train.csv")
    val = load_split(PIPELINE / "outputs/clf_val.csv")
    test = load_split(PIPELINE / "outputs/clf_test.csv")

    cont, cat_all = get_reduced_features()
    cb_features = cont + cat_all
    cat_indices = list(range(len(cont), len(cb_features)))

    y_train = train["target"].values
    y_val = val["target"].values
    w_val = val["weight"].values

    print("[2] Training V1-equivalent model...")
    model = CatBoostClassifier(
        iterations=1200, learning_rate=0.08, depth=6, l2_leaf_reg=1.0,
        random_seed=SEED, verbose=0, eval_metric="AUC",
        cat_features=cat_indices, task_type="CPU",
    )
    train_pool = Pool(train[cb_features], y_train, cat_features=cat_indices)
    val_pool = Pool(val[cb_features], y_val, cat_features=cat_indices)
    model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=80)

    y_prob_val = model.predict_proba(val[cb_features])[:, 1]

    # Also get seg labels for cross-analysis
    seg_full = pd.read_csv(PIPELINE / "outputs/stage7/stage7_results.json"
                           .replace("stage7_results.json", ""),
                           keep_default_na=False) if False else None
    # Load seg labels from stage7 results
    with open(PIPELINE / "outputs/stage7/stage7_results.json") as f:
        s7 = json.load(f)

    print("[3] Computing score bands...")
    bands = [
        ("A: Very High", 0.50, 1.01),
        ("B: High", 0.30, 0.50),
        ("C: Marginal", 0.15, 0.30),
        ("D: Low", 0.05, 0.15),
        ("E: Very Low", 0.00, 0.05),
    ]

    band_results = []
    for label, lo, hi in bands:
        mask = (y_prob_val >= lo) & (y_prob_val < hi)
        n = mask.sum()
        if n == 0:
            continue
        y_t = y_val[mask]
        w = w_val[mask]
        n_pos = y_t.sum()
        prec = n_pos / n if n > 0 else 0
        weighted_n = w.sum()
        entry = {
            "band": label, "lo": lo, "hi": hi,
            "n": int(n), "n_pos": int(n_pos),
            "precision": round(prec, 4),
            "pct_of_val": round(n / len(y_val) * 100, 1),
            "weighted_n": round(weighted_n, 0),
            "weighted_pct": round(weighted_n / w_val.sum() * 100, 1),
        }
        band_results.append(entry)
        print(f"  {label}: n={n:,} pos={n_pos} prec={prec:.3f} "
              f"({n/len(y_val)*100:.1f}%)")

    # Cumulative capture
    sorted_idx = np.argsort(-y_prob_val)
    cum_tp = np.cumsum(y_val[sorted_idx])
    total_pos = y_val.sum()

    capture_points = [100, 500, 1000, 1500, 2000, 3000, 5000]
    capture_results = []
    for k in capture_points:
        if k > len(y_val):
            break
        tp = int(cum_tp[k - 1])
        recall = tp / total_pos
        prec = tp / k
        threshold_at_k = float(y_prob_val[sorted_idx[k - 1]])
        capture_results.append({
            "top_k": k, "true_pos": tp, "recall": round(recall, 4),
            "precision": round(prec, 4), "threshold_at_k": round(threshold_at_k, 4),
        })
        print(f"  Top {k:,}: TP={tp}, recall={recall:.3f}, "
              f"prec={prec:.3f}, score>={threshold_at_k:.3f}")

    return {
        "bands": band_results,
        "cumulative_capture": capture_results,
        "val_n": len(y_val),
        "val_pos": int(total_pos),
        "score_stats": {
            "mean": round(float(y_prob_val.mean()), 4),
            "median": round(float(np.median(y_prob_val)), 4),
            "p90": round(float(np.percentile(y_prob_val, 90)), 4),
            "p95": round(float(np.percentile(y_prob_val, 95)), 4),
            "p99": round(float(np.percentile(y_prob_val, 99)), 4),
        },
    }, model, y_prob_val


# ═══════════════════════════════════════════════════════
# PART 2: SECOND-PASS SEGMENTATION (within working-age)
# ═══════════════════════════════════════════════════════

SEG2_CONTINUOUS = ["age", "weeks worked in year", "capital gains",
                   "dividends from stocks", "wage per hour"]
SEG2_CATEGORICAL = ["education", "marital stat", "sex",
                    "major occupation code", "major industry code",
                    "class of worker", "tax filer stat",
                    "own business or self employed",
                    "detailed household summary in household"]


def second_pass_segmentation():
    print()
    print("=" * 60)
    print("PART 2: Second-Pass Segmentation (Working-Age)")
    print("=" * 60)

    # Load full segmentation dataset
    print("[1] Loading seg_full.csv...")
    df = pd.read_csv(PIPELINE / "outputs/seg_full.csv",
                     keep_default_na=False, na_values=[])
    for col in NUMERIC_CODED_CAT:
        if col in df.columns:
            df[col] = df[col].astype(str)
    for col in CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "Missing")
    for col in CONTINUOUS_NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Reconstruct V1 macro labels to identify working-age segment
    # V1 seg 2 = working-age = ~46% of data
    # We'll identify by age + employment proxy
    # Actually, let's just re-run V1 K-Prototypes to get labels...
    # Faster: use the V1 segment characteristics to filter
    # Seg 0 (seniors): age >= 55 AND weeks_worked < 10 AND class_of_worker ~= "Not in universe"
    # Seg 1 (youth): age < 18 OR education = "Children"
    # Seg 2 (working-age): everyone else
    # This is an approximation but very close to V1 clustering

    print("[2] Identifying working-age segment (V1 Seg 2 approximation)...")
    youth_mask = (df["age"] < 18) | (df["education"] == "Children")
    senior_mask = (~youth_mask) & (df["age"] >= 55) & (df["weeks worked in year"] < 10)
    working_age_mask = ~youth_mask & ~senior_mask

    n_youth = youth_mask.sum()
    n_senior = senior_mask.sum()
    n_working = working_age_mask.sum()
    print(f"  Youth: {n_youth:,} ({n_youth/len(df)*100:.1f}%)")
    print(f"  Senior: {n_senior:,} ({n_senior/len(df)*100:.1f}%)")
    print(f"  Working-age: {n_working:,} ({n_working/len(df)*100:.1f}%)")

    seg2 = df[working_age_mask].reset_index(drop=True)

    # Prepare K-Prototypes input
    print("[3] Preparing second-pass features...")
    X_cont = seg2[SEG2_CONTINUOUS].copy()
    cont_means = X_cont.mean()
    cont_stds = X_cont.std().replace(0, 1)
    X_cont_scaled = (X_cont - cont_means) / cont_stds

    X_cat = seg2[SEG2_CATEGORICAL].copy().astype(str)
    X = pd.concat([X_cont_scaled, X_cat], axis=1)
    cat_indices = list(range(len(SEG2_CONTINUOUS),
                             len(SEG2_CONTINUOUS) + len(SEG2_CATEGORICAL)))

    # Subsample
    np.random.seed(SEED)
    sub_n = min(20000, len(seg2))
    idx = np.random.choice(len(seg2), sub_n, replace=False)
    X_sub = X.iloc[idx].reset_index(drop=True)

    # Evaluate k range
    print("[4] Evaluating k=3..6...")
    k_eval = []
    for k in range(3, 7):
        kp = KPrototypes(n_clusters=k, init="Cao", n_init=3,
                         max_iter=50, random_state=SEED, n_jobs=-1,
                         verbose=0, gamma=0.5)
        labels = kp.fit_predict(X_sub, categorical=cat_indices)
        cost = kp.cost_
        sizes = Counter(labels)
        min_pct = min(sizes.values()) / len(labels) * 100
        k_eval.append({"k": k, "cost": float(cost),
                       "min_cluster_pct": round(min_pct, 1)})
        print(f"    k={k}: cost={cost:.0f} min_cluster={min_pct:.1f}%")

    # Select k
    viable = [r for r in k_eval if r["min_cluster_pct"] >= 5.0]
    if viable:
        chosen_k = max(r["k"] for r in viable)
    else:
        chosen_k = max(k_eval, key=lambda r: r["min_cluster_pct"])["k"]
    print(f"  Selected k={chosen_k}")

    # Final fit
    print(f"[5] Final fit k={chosen_k} on subsample...")
    kp_final = KPrototypes(n_clusters=chosen_k, init="Cao", n_init=5,
                           max_iter=100, random_state=SEED, n_jobs=-1,
                           verbose=0, gamma=0.5)
    labels_sub = kp_final.fit_predict(X_sub, categorical=cat_indices)

    print("  Assigning full working-age segment...")
    labels_full = kp_final.predict(X, categorical=cat_indices)

    # Absorb micro-clusters
    threshold_n = len(seg2) * 0.03
    sizes = Counter(labels_full)
    micro = {c for c, n in sizes.items() if n < threshold_n}
    if micro:
        large = sorted(set(labels_full) - micro)
        centroids = {}
        for c in large:
            mask = labels_full == c
            centroids[c] = seg2.loc[mask, SEG2_CONTINUOUS].mean().values
        for mc in micro:
            mask = labels_full == mc
            mc_cent = seg2.loc[mask, SEG2_CONTINUOUS].mean().values
            dists = {c: np.linalg.norm(mc_cent - centroids[c]) for c in large}
            nearest = min(dists, key=dists.get)
            labels_full[mask] = nearest
            print(f"  Absorbed micro-cluster {mc} ({sizes[mc]} rows) -> {nearest}")
        unique = sorted(set(labels_full))
        remap = {old: new for new, old in enumerate(unique)}
        labels_full = np.array([remap[l] for l in labels_full])

    final_k = len(set(labels_full))
    print(f"  Final sub-segments: {final_k}")

    # Profile
    print("[6] Profiling sub-segments...")
    seg2["_subseg"] = labels_full
    target_rate_overall = seg2["_target"].mean()

    profiles = {}
    profile_cols = ["age", "education", "marital stat", "sex",
                    "major occupation code", "class of worker",
                    "tax filer stat", "weeks worked in year",
                    "own business or self employed",
                    "detailed household summary in household"]

    for sid in sorted(seg2["_subseg"].unique()):
        s = seg2[seg2["_subseg"] == sid]
        n = len(s)
        w = s["_weight"].sum()
        tr = s["_target"].mean()
        p = {
            "segment_id": int(sid), "raw_size": n,
            "raw_pct": round(n / len(seg2) * 100, 1),
            "weighted_pct": round(w / seg2["_weight"].sum() * 100, 1),
            "target_rate": round(tr * 100, 2),
            "enrichment_vs_seg2": round(tr / target_rate_overall, 2) if target_rate_overall > 0 else 0,
            "features": {},
        }
        for col in profile_cols:
            if col in CONTINUOUS_NUMERIC or col in ["weeks worked in year"]:
                p["features"][col] = {
                    "mean": round(float(s[col].mean()), 1),
                    "median": round(float(s[col].median()), 1),
                }
            else:
                top = s[col].value_counts().head(3)
                p["features"][col] = {
                    str(k): round(int(v) / n * 100, 1) for k, v in top.items()
                }
        profiles[int(sid)] = p
        print(f"  Sub-seg {sid}: n={n:,} ({p['raw_pct']}%) "
              f">50K={p['target_rate']}% enrich={p['enrichment_vs_seg2']}x")

    return {
        "working_age_n": len(seg2),
        "k_eval": k_eval,
        "chosen_k": chosen_k,
        "final_k": final_k,
        "profiles": profiles,
        "features_used": {
            "continuous": SEG2_CONTINUOUS,
            "categorical": SEG2_CATEGORICAL,
        },
    }


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    results = {}

    # Part 1
    score_data, model, y_prob_val = score_band_analysis()
    results["score_band_analysis"] = score_data

    # Part 2
    seg2_data = second_pass_segmentation()
    results["second_pass_segmentation"] = seg2_data

    # Save
    out_path = OUTDIR / "v2_compute_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
