# Classification Baseline

> Derived from: pipeline/outputs/stage5/BASELINE_METRICS.md, pipeline/outputs/stage5/CLASSIFIER_BASELINE_REPORT.md, TECHNICAL_APPENDIX.md

## Baseline Candidates

8 configurations tested: 2 model families x 2 feature sets x 2 training modes.

**Model families**: Logistic Regression (L2, saga solver) vs CatBoost (800 iterations, depth=6)

**Feature sets**: Full (40 features) vs Reduced (35 features, 5 sparse review columns removed)

**Training modes**: NoClsBal (standard) vs ClsBal (class_weight='balanced' for LR, scale_pos_weight for CatBoost)

## Validation Results

| Configuration | PR-AUC | ROC-AUC | F1 @0.5 |
|--------------|-------:|--------:|--------:|
| LR / Full / NoClsBal | 0.5978 | 0.9416 | 0.4835 |
| LR / Full / ClsBal | 0.5900 | 0.9412 | 0.4346 |
| LR / Reduced / NoClsBal | 0.5976 | 0.9416 | 0.4835 |
| LR / Reduced / ClsBal | 0.5898 | 0.9411 | 0.4348 |
| CB / Full / NoClsBal | 0.6865 | 0.9519 | 0.5719 |
| CB / Full / ClsBal | 0.6729 | 0.9521 | 0.4757 |
| **CB / Reduced / NoClsBal** | **0.6877** | **0.9517** | **0.5714** |
| CB / Reduced / ClsBal | 0.6735 | 0.9523 | 0.4783 |

## Key Findings

1. **CatBoost >> LR**: +0.09 PR-AUC. CatBoost handles the categorical-dominated feature set natively.
2. **Reduced >= Full**: Dropping 5 sparse review columns (92-99% "Not in universe") slightly improved performance. More features is not automatically better.
3. **NoClsBal > ClsBal**: Class balancing trades PR-AUC for recall at the cost of precision. For this task, threshold tuning is a better strategy than loss reweighting.

## Carry-Forward Candidate

**CB/Red/NoClsBal** advanced to Stage 6 for tuning.

## Survey-Weighted Evaluation Note

All configurations were evaluated under both unweighted and survey-weighted metrics. The same candidate won under both regimes. "ClsBal" refers to class-balanced training (label imbalance), NOT survey weighting (population representativeness). These are independent concepts documented explicitly in the Stage 5 governance fix.
