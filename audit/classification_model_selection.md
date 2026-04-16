# Classification Model Selection

> Derived from: pipeline/outputs/stage6/MODEL_SELECTION_REPORT.md, STAGE6_FINAL_METRICS.md, THRESHOLD_POLICY_REPORT.md, CALIBRATION_REPORT.md, FEATURE_INTERPRETATION_REPORT.md

## Stage 6 Tuning

27-configuration grid: depth x {4,6,8}, learning_rate x {0.03,0.05,0.08}, l2_leaf_reg x {1.0,3.0,5.0}. Iterations: 1200 with early stopping at 80.

**Selected**: depth=6, lr=0.08, l2_leaf_reg=1.0 (best_iteration=1194)

Improvement over Stage 5 baseline: +0.0055 PR-AUC (0.6877 -> 0.6932 on validation).

## Final Test Metrics

| Metric | Validation | Test |
|--------|-----------|------|
| PR-AUC | 0.6932 | 0.7008 |
| ROC-AUC | 0.9534 | 0.9565 |
| F1 (t=0.25) | 0.6299 | 0.6276 |
| Brier Score | 0.0315 | 0.0311 |

Results stable under survey-weighted evaluation (SW-PR-AUC: 0.6906 val, 0.7045 test).

## Threshold Policy

The default 0.5 threshold is suboptimal for rare-event classification (6.2% positive).

| Mode | Threshold | Precision | Recall | F1 | Use Case |
|------|-----------|-----------|--------|-----|----------|
| Precision-leaning | 0.45 | 0.726 | 0.510 | 0.599 | Expensive 1:1 outreach |
| **Balanced** | **0.25** | **0.585** | **0.683** | **0.630** | **General targeting** |
| Recall-leaning | 0.20 | 0.532 | 0.732 | 0.616 | Broad screening |

Threshold recommendations are identical under both unweighted and survey-weighted evaluation.

## Calibration

| Method | Brier Score |
|--------|------------|
| Uncalibrated | 0.0315 |
| Isotonic | 0.0317 |
| Platt | 0.0336 |

**Decision**: Not adopted. Uncalibrated probabilities are already well-calibrated. Neither method improved Brier score.

## Top Features

1. family members under 18 (26.5)
2. age (20.9)
3. veterans benefits (9.1)
4. weeks worked in year (7.0)
5. sex (5.1)
6. education (4.0)

Diverse mix of human-capital, employment, and household signals. No suspicious single-feature dominance. SHAP analysis confirms the same top tier.

## Framing

This classifier is a **targeting score**, not a truth machine. It ranks people by income likelihood. The business decision happens at the threshold layer — which error is more costly determines the operating point. The score is most valuable when combined with segment membership to customize the marketing approach.
