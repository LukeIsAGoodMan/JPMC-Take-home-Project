# Pipeline Design

> Derived from: README.md, SUBMISSION_SUMMARY.md, FINAL_REPORT.html

## End-to-End Architecture

```
census_bureau.jsonl
        |
    [Stage 4: preprocess.py]
        |
        +---> clf_train.csv / clf_val.csv / clf_test.csv
        |         |
        |     [Stage 5: classify_baseline.py]
        |         |  LR vs CatBoost, 8 configs
        |         |
        |     [Stage 6: classify_stage6.py]
        |         |  27-config tuning, threshold, calibration, SHAP
        |         |
        |         +---> Final classifier + threshold policy
        |
        +---> seg_full.csv
                  |
              [Stage 7: segment_stage7.py]
                  |  K-Prototypes, k eval, absorption
                  |
                  +---> 3 marketing segments
                  
    [Stage 8: packaging]
        |
        +---> README.md, CLIENT_REPORT.md, FINAL_REPORT.html, audit/
```

## Stage Dependencies

| Stage | Input | Output | Script |
|-------|-------|--------|--------|
| 4 | census_bureau.jsonl | clf splits + seg_full.csv + audit docs | preprocess.py |
| 5 | clf splits | Baseline metrics + carry-forward candidate | classify_baseline.py |
| 6 | clf splits | Tuned model + threshold + calibration + features | classify_stage6.py |
| 7 | seg_full.csv | 3 segments + profiles + playbook | segment_stage7.py |
| 8 | All outputs | Final submission package | Manual |

Stages 5-6 (classification) and Stage 7 (segmentation) are **independent tracks** that share the Stage 4 preprocessing foundation but do not depend on each other.

## Why Two Separate Tracks

The classifier and segmentation solve different problems:

- **Classifier**: "Is this person likely >$50K?" — a supervised scoring problem
- **Segmentation**: "What kind of person is this?" — an unsupervised grouping problem

They share preprocessing but differ in feature selection, methodology, and output. The two-layer design is more useful than either alone: score + segment = who to prioritize and how to approach them.

## Execution Order

```bash
cd pipeline/

# Stage 4: Preprocessing (must run first)
python preprocess.py --data ../datasource/census_bureau.jsonl --outdir outputs --seed 42

# Stage 5: Baselines (requires Stage 4 outputs)
python -u classify_baseline.py --datadir outputs --outdir outputs/stage5 --seed 42

# Stage 6: Tuning (requires Stage 4 outputs; uses Stage 5 for context only)
python -u classify_stage6.py --datadir outputs --outdir outputs/stage6 --seed 42

# Stage 7: Segmentation (requires Stage 4 outputs; independent of Stages 5-6)
python -u segment_stage7.py --datadir outputs --outdir outputs/stage7 --seed 42
```

All scripts are deterministic with seed=42.
