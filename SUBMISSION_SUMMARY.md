# Submission Summary

## What This Is

A two-track ML project on weighted CPS census data (199,523 records, 1994-1995):

1. **Income classifier** — predicts whether an individual earns >$50K
2. **Marketing segmentation** — identifies distinct population groups for retail targeting

The final deliverable is not "just a model." It is a two-layer targeting design: the classifier scores and prioritizes; the segmentation explains who people are and how to approach them.

## What to Read First

| Order | Document | Audience | Time |
|-------|----------|----------|------|
| 1 | **This file** | Everyone | 2 min |
| 2 | `CLIENT_REPORT.md` | Business reviewer | 10 min |
| 3 | `README.md` | Technical reviewer | 5 min |
| 4 | `TECHNICAL_APPENDIX.md` | Governance / deep dive | 15 min |
| 5 | `pipeline/outputs/stage6/STAGE6_FINAL_METRICS.md` | Metric detail | 3 min |
| 6 | `pipeline/outputs/stage7/SEGMENT_PROFILES.md` | Segment detail | 5 min |

## Final Classifier

**CatBoost** on a reduced feature set (31 of 40 features, 5 sparse columns removed).

| Metric | Validation | Test |
|--------|-----------|------|
| PR-AUC | 0.6932 | 0.7008 |
| ROC-AUC | 0.9534 | 0.9565 |
| F1 (t=0.25) | 0.6299 | 0.6276 |
| Brier | 0.0315 | 0.0311 |

Threshold is a business-policy decision, not a model constant:

| Operating Mode | Threshold | Precision | Recall |
|---------------|-----------|-----------|--------|
| Precision-leaning | 0.45 | 0.73 | 0.51 |
| Balanced (default) | 0.25 | 0.58 | 0.68 |
| Recall-leaning | 0.20 | 0.53 | 0.73 |

## Final Segmentation

3 segments via K-Prototypes on mixed-type features. Target and weight excluded from clustering input.

| Segment | Population Share | >50K Rate |
|---------|-----------------|-----------|
| Senior/Retired Householders | 20% | 2.2% |
| Youth/Dependent Non-Workforce | 33% | 0.05% |
| Mid-Career Working Householders | 47% | 12.5% |

## Key Business Insight

The classifier tells you *who to prioritize*. The segmentation tells you *how to approach them*. Neither alone is the full answer — together they form a targeting design that a retail client can act on.

## Scripts

| Script | What it does |
|--------|-------------|
| `pipeline/preprocess.py` | Stage 4: preprocessing + train/val/test splits |
| `pipeline/classify_baseline.py` | Stage 5: baseline models (LR + CatBoost grid) |
| `pipeline/classify_stage6.py` | Stage 6: tuning, threshold, calibration, interpretability |
| `pipeline/segment_stage7.py` | Stage 7: segmentation modeling |
| `datasource/profile_jsonl.py` | Data profiling utility |
