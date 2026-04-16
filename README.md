# Census Income Classification & Marketing Segmentation

A take-home ML project: predict whether income exceeds $50K and segment the population for retail marketing, using weighted CPS census data (199,523 records, 1994-1995).

## Project Objective

Build two complementary tools for a retail client:

1. **Income classifier** — a scoring model that ranks individuals by likelihood of earning >$50K, enabling prioritized targeting
2. **Population segmentation** — interpretable groups based on life-stage, employment, and household patterns, enabling differentiated marketing approaches

The two layers work together: the classifier answers *who to prioritize*, the segmentation answers *how to approach them*.

## Dataset

- **Source**: Current Population Survey (CPS), 1994-1995
- **Records**: 199,523
- **Features**: 42 columns (demographic, employment, household, financial)
- **Target**: binary income label (`<= 50K` vs `> 50K`), ~6.2% positive class
- **Weight**: CPS population weight for survey-representative evaluation

## Repository Structure

```
jpmc/
  SUBMISSION_SUMMARY.md        <- start here
  README.md                    <- this file
  CLIENT_REPORT.md             <- business-facing narrative
  TECHNICAL_APPENDIX.md        <- governance / interview-defense doc
  datasource/
    census_bureau.jsonl         <- full dataset (199,523 rows)
    schema.json                 <- column schema
    profile_jsonl.py            <- data profiling script
    summary_report_full.md      <- full-data profiling output
  pipeline/
    preprocess.py               <- Stage 4: preprocessing + splits
    classify_baseline.py        <- Stage 5: baseline models
    classify_stage6.py          <- Stage 6: tuning + threshold + calibration
    segment_stage7.py           <- Stage 7: segmentation
    outputs/
      clf_train.csv             <- train split (139,665 rows)
      clf_val.csv               <- validation split (29,929 rows)
      clf_test.csv              <- test split (29,929 rows)
      seg_full.csv              <- segmentation-ready dataset
      column_treatment.md       <- per-column preprocessing decisions
      PREPROCESSING_AUDIT.md    <- preprocessing governance audit
      split_summary.md          <- train/val/test distribution audit
      stage5/                   <- baseline comparison artifacts
      stage6/                   <- final classifier artifacts
      stage7/                   <- segmentation artifacts
```

## How to Run

All scripts assume Python 3.11+ with pandas, scikit-learn, catboost, kmodes, and shap installed.

```bash
# Stage 4: Preprocessing (produces train/val/test splits + segmentation dataset)
cd pipeline/
python preprocess.py --data ../datasource/census_bureau.jsonl --outdir outputs --seed 42

# Stage 5: Baseline models (LR + CatBoost, 8-config grid)
python -u classify_baseline.py --datadir outputs --outdir outputs/stage5 --seed 42

# Stage 6: Tuning + threshold + calibration + interpretability
python -u classify_stage6.py --datadir outputs --outdir outputs/stage6 --seed 42

# Stage 7: Segmentation
python -u segment_stage7.py --datadir outputs --outdir outputs/stage7 --seed 42
```

## Final Classifier

**CatBoost** (depth=6, lr=0.08, l2_leaf_reg=1.0) on a reduced feature set (31 features).

| Metric | Validation | Test |
|--------|-----------|------|
| PR-AUC | 0.6932 | 0.7008 |
| ROC-AUC | 0.9534 | 0.9565 |
| F1 (threshold=0.25) | 0.6299 | 0.6276 |
| Brier Score | 0.0315 | 0.0311 |

Results are consistent under both unweighted and survey-weighted evaluation.

### Why CatBoost

- Dataset is dominated by categorical variables (24 of 31 features)
- CatBoost handles categoricals natively without one-hot encoding
- Outperformed Logistic Regression by +0.09 PR-AUC in Stage 5 baseline comparison

### Why PR-AUC Over Accuracy

The positive class is ~6.2% of the data. A model that predicts "<=50K" for everyone achieves 93.8% accuracy. PR-AUC measures the model's ability to find the rare positive class — the actual business task.

## Final Segmentation

3 segments via K-Prototypes clustering on mixed-type features. Target and weight were excluded from clustering input and used only for post-hoc profiling.

| Segment | Share | >50K Rate | Marketing Fit |
|---------|-------|-----------|---------------|
| Senior/Retired Householders | 20% | 2.2% | Retirement products, estate planning |
| Youth/Dependent Non-Workforce | 33% | 0.05% | Family-indirect, youth savings |
| Mid-Career Working Householders | 47% | 12.5% | Premium products, wealth management |

## Key Conclusions

1. **Threshold is a business decision**: The default 0.5 cutoff wastes most of the model's value. Operating at threshold 0.25 (balanced) or 0.20 (recall-leaning) dramatically improves the usefulness of predictions.

2. **Income is a proxy**: The >$50K label is a coarse proxy for what a retail client actually cares about (purchasing power, product affinity, lifetime value). The classifier should be treated as a prioritization tool, not a truth machine.

3. **Simpler features won**: Dropping 5 sparse review columns (92-99% "Not in universe") slightly improved performance. More features is not automatically better.

4. **Calibration was unnecessary**: The model's predicted probabilities are already well-calibrated (Brier 0.031). No post-hoc calibration needed.

5. **Survey weights matter for interpretation, not training**: CPS population weights are used for population-representative evaluation and segment sizing, not as training sample weights.

## Assumptions and Limitations

- Data is from 1994-1995; real deployment would require current data
- Income threshold ($50K in 1994 dollars) would need inflation adjustment
- No external validation dataset available
- Segmentation is a useful lens, not ground truth — alternative feature subsets would produce different valid segments
- The project intentionally prioritizes auditability and business clarity over maximum model complexity

## Detailed Documentation

- Business narrative: `CLIENT_REPORT.md`
- Technical governance: `TECHNICAL_APPENDIX.md`
- Classifier metrics: `pipeline/outputs/stage6/STAGE6_FINAL_METRICS.md`
- Threshold policy: `pipeline/outputs/stage6/THRESHOLD_POLICY_REPORT.md`
- Feature importance: `pipeline/outputs/stage6/FEATURE_INTERPRETATION_REPORT.md`
- Segment profiles: `pipeline/outputs/stage7/SEGMENT_PROFILES.md`
- Segmentation playbook: `pipeline/outputs/stage7/SEGMENTATION_ACTION_PLAYBOOK.md`
