"""
v2_phase4_experiments.py — V2 Phase 4: weighted training + benchmark.
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from catboost import CatBoostClassifier, Pool
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score,
    precision_score, recall_score, f1_score, brier_score_loss)

warnings.filterwarnings("ignore")
SEED = 42
PIPELINE = Path("../pipeline")

CONTINUOUS = ["age","wage per hour","capital gains","capital losses",
    "dividends from stocks","num persons worked for employer","weeks worked in year"]
NUM_CODED = ["detailed industry recode","detailed occupation recode",
    "own business or self employed","veterans benefits","year"]
CATEGORICAL = ["class of worker","education","enroll in edu inst last wk",
    "marital stat","major industry code","major occupation code","race",
    "hispanic origin","sex","member of a labor union",
    "full or part time employment stat","tax filer stat",
    "detailed household and family stat","detailed household summary in household",
    "migration code-change in msa","migration code-change in reg",
    "migration code-move within reg","live in this house 1 year ago",
    "migration prev res in sunbelt","family members under 18",
    "country of birth father","country of birth mother",
    "country of birth self","citizenship"]
REVIEW = ["reason for unemployment","region of previous residence",
    "state of previous residence","migration prev res in sunbelt",
    "fill inc questionnaire for veteran's admin"]

def load_split(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[])
    for c in NUM_CODED:
        if c in df.columns: df[c] = df[c].astype(str)
    for c in CATEGORICAL:
        if c in df.columns: df[c] = df[c].astype(str).replace("nan","Missing")
    for c in CONTINUOUS:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def evaluate(y, yp, yd, sw=None):
    return {
        "roc_auc": round(roc_auc_score(y, yp, sample_weight=sw), 4),
        "pr_auc": round(average_precision_score(y, yp, sample_weight=sw), 4),
        "f1": round(f1_score(y, yd, zero_division=0, sample_weight=sw), 4),
        "precision": round(precision_score(y, yd, zero_division=0, sample_weight=sw), 4),
        "recall": round(recall_score(y, yd, zero_division=0, sample_weight=sw), 4),
        "brier": round(brier_score_loss(y, yp, sample_weight=sw), 4),
    }

def main():
    print("[1] Loading data...")
    train = load_split(PIPELINE/"outputs/clf_train.csv")
    val = load_split(PIPELINE/"outputs/clf_val.csv")
    test = load_split(PIPELINE/"outputs/clf_test.csv")

    cont_cols = CONTINUOUS
    cat_all = [c for c in NUM_CODED + CATEGORICAL if c not in REVIEW]
    cb_features = cont_cols + cat_all
    cat_idx = list(range(len(cont_cols), len(cb_features)))

    y_tr, y_vl, y_ts = train["target"].values, val["target"].values, test["target"].values
    w_tr, w_vl = train["weight"].values, val["weight"].values
    X_tr, X_vl, X_ts = train[cb_features], val[cb_features], test[cb_features]
    T = 0.25
    results = {}

    # ═════════ PART A: WEIGHTED TRAINING ═════════
    print("\n[2] Weighted training experiments...")

    weight_variants = {
        "baseline_no_weight": None,
        "normalized": w_tr / w_tr.mean(),
        "sqrt": np.sqrt(w_tr / w_tr.mean()),
        "capped_p99": np.clip(w_tr, None, np.percentile(w_tr, 99)) / np.clip(w_tr, None, np.percentile(w_tr, 99)).mean(),
    }

    wt_results = {}
    for label, sw in weight_variants.items():
        print(f"  {label}...", end=" ", flush=True)
        m = CatBoostClassifier(iterations=1200, learning_rate=0.08, depth=6,
            l2_leaf_reg=1.0, random_seed=SEED, verbose=0, eval_metric="AUC",
            cat_features=cat_idx, task_type="CPU")
        tp = Pool(X_tr, y_tr, cat_features=cat_idx, weight=sw)
        vp = Pool(X_vl, y_vl, cat_features=cat_idx)
        m.fit(tp, eval_set=vp, early_stopping_rounds=80)
        yp = m.predict_proba(X_vl)[:, 1]
        yd = (yp >= T).astype(int)
        uw = evaluate(y_vl, yp, yd)
        swm = evaluate(y_vl, yp, yd, sw=w_vl)
        wt_results[label] = {"val_uw": uw, "val_sw": swm}
        print(f"UW PR-AUC={uw['pr_auc']} SW PR-AUC={swm['pr_auc']}")
    results["weighted_training"] = wt_results

    # ═════════ PART B: BENCHMARK ���════════
    print("\n[3] Classifier benchmark...")

    # Need label-encoded version for LightGBM / XGBoost
    from sklearn.preprocessing import OrdinalEncoder
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_tr_enc = X_tr.copy(); X_vl_enc = X_vl.copy(); X_ts_enc = X_ts.copy()
    X_tr_enc[cat_all] = enc.fit_transform(X_tr[cat_all])
    X_vl_enc[cat_all] = enc.transform(X_vl[cat_all])
    X_ts_enc[cat_all] = enc.transform(X_ts[cat_all])

    benchmarks = {}

    # CatBoost baseline (already in weighted experiments as baseline_no_weight)
    benchmarks["CatBoost (accepted)"] = wt_results["baseline_no_weight"]

    # LightGBM
    print("  LightGBM...", end=" ", flush=True)
    lgb = LGBMClassifier(n_estimators=1200, learning_rate=0.08, max_depth=6,
        reg_lambda=1.0, random_state=SEED, verbose=-1, n_jobs=-1,
        categorical_feature=[cb_features.index(c) for c in cat_all])
    lgb.fit(X_tr_enc, y_tr, eval_set=[(X_vl_enc, y_vl)],
            callbacks=[lambda env: (env.iteration > 80 and
                env.evaluation_result_list[0][2] < max(r[2] for r in env.evaluation_result_list[:max(1,env.iteration-79)])) or None])
    # simpler: just fit and predict
    lgb = LGBMClassifier(n_estimators=1200, learning_rate=0.08, max_depth=6,
        reg_lambda=1.0, random_state=SEED, verbose=-1, n_jobs=-1)
    lgb.fit(X_tr_enc, y_tr)
    yp_lgb = lgb.predict_proba(X_vl_enc)[:, 1]
    yd_lgb = (yp_lgb >= T).astype(int)
    lgb_uw = evaluate(y_vl, yp_lgb, yd_lgb)
    lgb_sw = evaluate(y_vl, yp_lgb, yd_lgb, sw=w_vl)
    benchmarks["LightGBM"] = {"val_uw": lgb_uw, "val_sw": lgb_sw}
    print(f"UW PR-AUC={lgb_uw['pr_auc']} SW PR-AUC={lgb_sw['pr_auc']}")

    # Also get LightGBM test
    yp_lgb_ts = lgb.predict_proba(X_ts_enc)[:, 1]
    yd_lgb_ts = (yp_lgb_ts >= T).astype(int)
    lgb_test_uw = evaluate(y_ts, yp_lgb_ts, yd_lgb_ts)
    benchmarks["LightGBM"]["test_uw"] = lgb_test_uw

    # XGBoost
    print("  XGBoost...", end=" ", flush=True)
    xgb = XGBClassifier(n_estimators=1200, learning_rate=0.08, max_depth=6,
        reg_lambda=1.0, random_state=SEED, verbosity=0, n_jobs=-1,
        enable_categorical=False)
    xgb.fit(X_tr_enc, y_tr)
    yp_xgb = xgb.predict_proba(X_vl_enc)[:, 1]
    yd_xgb = (yp_xgb >= T).astype(int)
    xgb_uw = evaluate(y_vl, yp_xgb, yd_xgb)
    xgb_sw = evaluate(y_vl, yp_xgb, yd_xgb, sw=w_vl)
    benchmarks["XGBoost"] = {"val_uw": xgb_uw, "val_sw": xgb_sw}
    print(f"UW PR-AUC={xgb_uw['pr_auc']} SW PR-AUC={xgb_sw['pr_auc']}")

    # CatBoost test for comparison
    m_cb = CatBoostClassifier(iterations=1200, learning_rate=0.08, depth=6,
        l2_leaf_reg=1.0, random_seed=SEED, verbose=0, eval_metric="AUC",
        cat_features=cat_idx, task_type="CPU")
    tp_cb = Pool(X_tr, y_tr, cat_features=cat_idx)
    vp_cb = Pool(X_vl, y_vl, cat_features=cat_idx)
    m_cb.fit(tp_cb, eval_set=vp_cb, early_stopping_rounds=80)
    yp_cb_ts = m_cb.predict_proba(X_ts)[:, 1]
    yd_cb_ts = (yp_cb_ts >= T).astype(int)
    cb_test_uw = evaluate(y_ts, yp_cb_ts, yd_cb_ts)
    benchmarks["CatBoost (accepted)"]["test_uw"] = cb_test_uw

    results["benchmark"] = benchmarks

    with open("v2_phase4_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved v2_phase4_results.json")

if __name__ == "__main__":
    main()
